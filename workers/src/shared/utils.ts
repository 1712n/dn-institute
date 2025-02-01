import { config } from '../config';

export interface WebContent {
  title: string;
  content: string;
  url: string;
}

export interface ArticleMetadata {
  targetEntities: string[];
  summary: string;
}

export interface LanguageCheckResult {
  matches: Array<{
    message: string;
    offset: number;
    length: number;
    context: {
      text: string;
      offset: number;
      length: number;
    };
    rule: {
      id: string;
      description: string;
      category: string;
    };
  }>;
}

class ContentHandler {
  content: string = '';
  
  text(text: Text) {
    this.content += text.text;
  }
}

export async function scrapeUrl(url: string): Promise<WebContent | null> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch URL: ${response.statusText}`);
    }

    const titleHandler = new ContentHandler();
    const contentHandler = new ContentHandler();

    const rewriter = new HTMLRewriter()
      .on('title', titleHandler)
      .on('article, main, [role="main"], .content, #content, .post-content, .article-content', contentHandler);

    await rewriter.transform(response).text();

    let { title, content } = {
      title: titleHandler.content,
      content: contentHandler.content || ''
    };

    // Clean content
    content = cleanContent(content);
    title = cleanContent(title);

    return { title, content, url };
  } catch (error) {
    console.error('Error scraping URL:', error);
    return null;
  }
}

export function cleanContent(text: string): string {
  return text
    .replace(/\\s+/g, ' ')
    .replace(/[\\r\\n]+/g, '\\n')
    .trim();
}

export function extractBetweenTags(tag: string, text: string): string[] {
  const regex = new RegExp(`<${tag}\\s*>([\\s\\S]*?)</${tag}>`, 'g');
  const matches = [...text.matchAll(regex)];
  return matches.map(match => match[1].trim());
}

export function formatSearchResults(results: WebContent[]): string {
  return results
    .map((result, index) => 
      `[${index + 1}] ${result.title}\\n${result.url}\\n${result.content}`
    )
    .join('\\n\\n');
}

export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = config.MAX_RETRIES,
  delay: number = config.RETRY_DELAY
): Promise<T> {
  let lastError: Error | null = null;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }
  
  throw lastError;
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export function extractArticleMetadata(text: string): ArticleMetadata {
  // Extract target entities
  const targetMatch = text.match(/target-entities:\s*(.*?)\n/);
  const targetEntities = targetMatch ? 
    targetMatch[1].split(',').map(e => e.trim()) : [];

  // Extract summary
  const summaryMatch = text.match(/## Summary\n([\s\S]*?)(?=##|$)/);
  const summary = summaryMatch ? summaryMatch[1].trim() : '';

  return { targetEntities, summary };
}

export async function getTargetEntities(url: string): Promise<string[]> {
  try {
    const response = await fetch(`${url}/attacks/posts/target-entities/`);
    if (!response.ok) return [];

    const titleHandler = new ContentHandler();
    const rewriter = new HTMLRewriter()
      .on('.section-item', titleHandler);

    await rewriter.transform(response).text();
    
    return titleHandler.content
      .split('\n')
      .map(line => line.trim())
      .filter(Boolean);
  } catch (error) {
    console.error('Error fetching target entities:', error);
    return [];
  }
}

export async function checkLanguage(text: string): Promise<LanguageCheckResult> {
  try {
    const response = await fetch('https://api.languagetool.org/v2/check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        text,
        language: 'en-US',
      }).toString(),
    });

    if (!response.ok) {
      throw new Error('Language check failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Language check error:', error);
    return { matches: [] };
  }
}

export function countTokens(text: string): number {
  // Simple word-based token count (can be replaced with a more sophisticated tokenizer)
  return text.split(/\s+/).length;
}

export function trimText(text: string, maxTokens: number): string {
  const tokens = text.split(/\s+/);
  if (tokens.length <= maxTokens) return text;
  return tokens.slice(0, maxTokens).join(' ') + '...';
}

export function removePlusMarkers(text: string): string {
  return text.replace(/^\+\s*/gm, '');
}

export function parseDiff(diff: string): Array<{ header: string; body: Array<{ body: string }> }> {
  const sections = diff.split(/^diff --git /m).filter(Boolean);
  return sections.map(section => {
    const [header, ...bodyParts] = section.split('@@');
    const body = bodyParts.map(part => ({ body: part.trim() }));
    return { header, body };
  });
} 