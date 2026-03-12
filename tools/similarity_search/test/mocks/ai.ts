// 🌰 Mock AI service for testing
export class MockAI {
  async run(model: string, input: any) {
    // 🌰 Return mock embedding vector
    return {
      data: [[
        0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
        0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 0.05,
      ]],
      shape: [1, 20],
    };
  }
}