// 🌰 Mock AI service for testing
export const mockAIService = {
  run: async (model: string, input: { text: string }) => {
    // 🌰 Generate deterministic mock embeddings
    const text = input.text;
    const hash = text.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    // 🌰 Return mock embedding vector
    const embedding = Array.from({ length: 768 }, (_, i) => 
      Math.sin(hash + i) * 0.5 + 0.5);
    return { data: [embedding] };
  }
};