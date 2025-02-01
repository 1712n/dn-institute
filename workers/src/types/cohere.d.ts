declare module 'cohere' {
  export interface GenerateResponse {
    generations: Array<{
      text: string;
    }>;
  }

  export interface EmbedResponse {
    embeddings: number[][];
  }

  export interface CohereClient {
    generate(params: {
      prompt: string;
      model: string;
      temperature: number;
      maxTokens: number;
    }): Promise<GenerateResponse>;
    embed(params: {
      texts: string[];
      model: string;
    }): Promise<EmbedResponse>;
  }

  export default {
    Client: class {
      constructor(apiKey: string);
      generate(params: {
        prompt: string;
        model: string;
        temperature: number;
        maxTokens: number;
      }): Promise<GenerateResponse>;
      embed(params: {
        texts: string[];
        model: string;
      }): Promise<EmbedResponse>;
    }
  }
} 