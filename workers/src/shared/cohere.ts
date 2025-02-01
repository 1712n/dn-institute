import cohere, { GenerateResponse, EmbedResponse } from 'cohere';
import { config } from '../config';
import { WebContent, scrapeUrl, retry, extractBetweenTags, formatSearchResults, truncateText, extractArticleMetadata, getTargetEntities, checkLanguage, LanguageCheckResult, countTokens, trimText, removePlusMarkers, parseDiff } from './utils';

interface SearchResult {
  content: string;
  url?: string;
}

interface BraveSearchResponse {
  web: {
    results: Array<{
      title: string;
      description: string;
      url: string;
    }>;
  };
}

interface FactCheckResult {
  isFactual: boolean;
  explanation: string;
  source: string;
}

interface DuplicationResult {
  isDuplicate: boolean;
  similarity: number;
  explanation: string;
}

interface ArticleValidation {
  isValid: boolean;
  targetEntityValid: boolean;
  factualAccuracy: FactCheckResult[];
  duplicationCheck: DuplicationResult | null;
  languageCheck: LanguageCheckResult;
  errors: string[];
  warnings: string[];
}

export class CohereService {
  private client: any;
  private searchApiKey: string;

  constructor(apiKey: string, searchApiKey: string) {
    this.client = new cohere.Client(apiKey);
    this.searchApiKey = searchApiKey;
  }

  private async extractStatements(text: string): Promise<string[]> {
    const response = await retry(() => 
      this.client.generate({
        prompt: config.EXTRACTING_PROMPT + `\\n${text}`,
        model: config.COHERE_MODEL,
        temperature: config.COHERE_TEMPERATURE,
        maxTokens: config.COHERE_MAX_TOKENS
      })
    ) as GenerateResponse;

    const statements = extractBetweenTags('statement', response.generations[0].text);
    return statements;
  }

  private async searchWeb(query: string): Promise<WebContent[]> {
    const headers = {
      'Accept': 'application/json',
      'X-Subscription-Token': this.searchApiKey
    };

    const response = await retry(() => 
      fetch(
        `${config.BRAVE_SEARCH_ENDPOINT}?q=${encodeURIComponent(query)}&count=${config.SEARCH_MAX_RESULTS}`,
        { headers }
      )
    );

    if (!response.ok) {
      throw new Error('Search request failed');
    }

    const data = await response.json() as BraveSearchResponse;
    const results: WebContent[] = [];

    for (const result of data.web.results) {
      const content = await scrapeUrl(result.url);
      if (content) {
        results.push(content);
      }
    }

    return results;
  }

  private async verifyStatement(statement: string): Promise<FactCheckResult> {
    const searchResults = await this.searchWeb(statement);
    const formattedResults = formatSearchResults(searchResults);
    
    const response = await retry(() => 
      this.client.generate({
        prompt: config.VERIFICATION_PROMPT
          .replace('{statement}', statement)
          .replace('{searchResults}', formattedResults),
        model: config.COHERE_MODEL,
        temperature: config.COHERE_TEMPERATURE,
        maxTokens: config.COHERE_MAX_TOKENS
      })
    ) as GenerateResponse;

    try {
      return JSON.parse(response.generations[0].text);
    } catch (error) {
      return {
        isFactual: false,
        explanation: 'Could not verify statement',
        source: 'None'
      };
    }
  }

  async checkDuplication(newArticle: string, existingArticle: string): Promise<DuplicationResult> {
    // First, get embeddings for both articles
    const embeddings = await retry(() => 
      this.client.embed({
        texts: [newArticle, existingArticle],
        model: 'embed-english-v3.0'
      })
    ) as EmbedResponse;

    // Calculate cosine similarity between embeddings
    const similarity = this.calculateCosineSimilarity(
      embeddings.embeddings[0],
      embeddings.embeddings[1]
    );

    // If similarity is high, do a detailed comparison
    if (similarity > config.SUMMARIZE_THRESHOLD) {
      const response = await retry(() => 
        this.client.generate({
          prompt: config.DUPLICATION_PROMPT
            .replace('{newArticle}', truncateText(newArticle, 1000))
            .replace('{existingArticle}', truncateText(existingArticle, 1000)),
          model: config.COHERE_MODEL,
          temperature: config.COHERE_TEMPERATURE,
          maxTokens: config.COHERE_MAX_TOKENS
        })
      ) as GenerateResponse;

      try {
        const result = JSON.parse(response.generations[0].text);
        return {
          ...result,
          similarity
        };
      } catch (error) {
        console.error('Error parsing duplication check result:', error);
      }
    }

    return {
      isDuplicate: false,
      similarity,
      explanation: 'Articles are sufficiently different'
    };
  }

  private calculateCosineSimilarity(a: number[], b: number[]): number {
    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
    return dotProduct / (magnitudeA * magnitudeB);
  }

  async checkArticle(text: string): Promise<string> {
    try {
      // Extract factual statements
      const statements = await this.extractStatements(text);
      
      // Verify each statement
      const verificationResults = await Promise.all(
        statements.map(statement => this.verifyStatement(statement))
      );

      // Format results as a GitHub comment
      const comment = [
        '## Article Check Results\n',
        '### Factual Accuracy Review\n'
      ];

      statements.forEach((statement, index) => {
        const result = verificationResults[index];
        comment.push(
          `#### Statement ${index + 1}:\n`,
          `> ${statement}\n\n`,
          `${result.isFactual ? '✅' : '❌'} **Verdict**: ${result.isFactual ? 'Verified' : 'Not Verified'}\n\n`,
          `**Explanation**: ${result.explanation}\n`,
          `**Source**: ${result.source === 'None' ? 'No source found' : result.source}\n\n`
        );
      });

      comment.push('---\n*Checked with Cohere AI*');
      
      return comment.join('');
    } catch (error) {
      console.error('Error checking article:', error);
      throw new Error('Failed to check article');
    }
  }

  async analyzeText(text: string): Promise<string> {
    try {
      const response = await this.client.generate({
        prompt: text,
        maxTokens: 500,
        temperature: 0.7,
        model: 'command',
      });

      return response.generations[0].text;
    } catch (error) {
      console.error('Error analyzing text with Cohere:', error);
      throw new Error('Failed to analyze text');
    }
  }

  async checkFactualAccuracy(text: string): Promise<{
    isFactual: boolean;
    explanation: string;
  }> {
    try {
      const prompt = `Please analyze the following text for factual accuracy. 
      Respond with a JSON object containing 'isFactual' (boolean) and 'explanation' (string).
      Text to analyze: ${text}`;

      const response = await this.client.generate({
        prompt,
        maxTokens: 1000,
        temperature: 0.3,
        model: 'command',
      });

      const result = JSON.parse(response.generations[0].text);
      return {
        isFactual: result.isFactual,
        explanation: result.explanation,
      };
    } catch (error) {
      console.error('Error checking factual accuracy:', error);
      throw new Error('Failed to check factual accuracy');
    }
  }

  async detectPlagiarism(text: string): Promise<{
    isPlagiarized: boolean;
    similarityScore: number;
    matches: string[];
  }> {
    try {
      const response = await this.client.embed({
        texts: [text],
        model: 'embed-english-v3.0',
      });

      // Here you would typically compare the embedding with a database of known content
      // For this example, we're returning a placeholder response
      return {
        isPlagiarized: false,
        similarityScore: 0,
        matches: [],
      };
    } catch (error) {
      console.error('Error detecting plagiarism:', error);
      throw new Error('Failed to detect plagiarism');
    }
  }

  async validateArticle(text: string, baseUrl: string): Promise<ArticleValidation> {
    const result: ArticleValidation = {
      isValid: true,
      targetEntityValid: false,
      factualAccuracy: [],
      duplicationCheck: null,
      languageCheck: { matches: [] },
      errors: [],
      warnings: []
    };

    try {
      // Clean and prepare text
      text = removePlusMarkers(text);
      
      // Extract metadata
      const metadata = extractArticleMetadata(text);
      
      // Check token length
      const tokenCount = countTokens(metadata.summary);
      if (tokenCount > config.MAX_TOKENS_TO_READ) {
        result.warnings.push(`Article exceeds maximum token length (${tokenCount} > ${config.MAX_TOKENS_TO_READ})`);
        metadata.summary = trimText(metadata.summary, config.MAX_TOKENS_TO_READ);
      }

      // Validate target entities
      const validTargets = await getTargetEntities(baseUrl);
      const hasValidTarget = metadata.targetEntities.some(target => 
        validTargets.includes(target)
      );

      if (!hasValidTarget) {
        result.isValid = false;
        result.errors.push('Invalid or missing target entity');
      }
      result.targetEntityValid = hasValidTarget;

      // Language check
      result.languageCheck = await checkLanguage(metadata.summary);
      if (result.languageCheck.matches.length > 0) {
        result.warnings.push(`Found ${result.languageCheck.matches.length} language issues`);
      }

      // Check factual accuracy
      const statements = await this.extractStatements(metadata.summary);
      result.factualAccuracy = await Promise.all(
        statements.map(statement => this.verifyStatement(statement))
      );

      // Check overall factual accuracy
      const inaccurateStatements = result.factualAccuracy.filter(r => !r.isFactual);
      if (inaccurateStatements.length > 0) {
        result.isValid = false;
        result.errors.push(`Found ${inaccurateStatements.length} inaccurate statements`);
      }

      // Check for duplicates if target is valid
      if (hasValidTarget) {
        const existingContent = await this.getExistingContent(
          baseUrl,
          metadata.targetEntities[0]
        );

        if (existingContent) {
          result.duplicationCheck = await this.checkDuplication(
            metadata.summary,
            existingContent
          );
          
          if (result.duplicationCheck.isDuplicate) {
            result.isValid = false;
            result.errors.push('Duplicate content detected');
          } else if (result.duplicationCheck.similarity > config.SUMMARIZE_THRESHOLD / 2) {
            result.warnings.push(`High content similarity (${Math.round(result.duplicationCheck.similarity * 100)}%)`);
          }
        }
      }

      return result;
    } catch (error) {
      console.error('Error validating article:', error);
      throw new Error('Failed to validate article');
    }
  }

  private async getExistingContent(baseUrl: string, targetEntity: string): Promise<string | null> {
    try {
      const url = `${baseUrl}/attacks/posts/target-entities/${targetEntity.replace(/\s+/g, '-')}`;
      const content = await scrapeUrl(url);
      return content?.content || null;
    } catch (error) {
      console.error('Error fetching existing content:', error);
      return null;
    }
  }
} 