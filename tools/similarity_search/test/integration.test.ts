import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { unstable_dev } from "wrangler";
import type { UnstableDevWorker } from "wrangler";

describe("🌰 Similarity Search API Integration Tests", () => {
  let worker: UnstableDevWorker;

  beforeEach(async () => {
    // 🌰 Start the worker in dev mode for testing
    worker = await unstable_dev("src/index.ts", {
      experimental: { disableExperimentalWarning: true },
      vars: {
        VECTORIZE_INDEX: "test-index",
        AI: "mock-ai",
      },
    });
  });

  afterEach(async () => {
    // 🌰 Clean up the worker
    if (worker) {
      await worker.stop();
    }
  });

  describe("🌰 Health Check Endpoint", () => {
    it("should return healthy status", async () => {
      const resp = await worker.fetch("/health");
      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(data).toEqual({ status: "healthy" });
    });
  });

  describe("🌰 Similarity Search Endpoint", () => {
    it("should return similarity scores for valid text", async () => {
      const testText = "This is a test message about blockchain technology";
      
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: testText }),
      });

      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(data).toHaveProperty("similarities");
      expect(Array.isArray(data.similarities)).toBe(true);
      expect(data).toHaveProperty("query");
      expect(data.query).toBe(testText);
    });

    it("should handle empty text gracefully", async () => {
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "" }),
      });

      expect(resp.status).toBe(400);
      
      const data = await resp.json();
      expect(data).toHaveProperty("error");
      expect(data.error).toContain("text is required");
    });

    it("should handle missing text parameter", async () => {
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });

      expect(resp.status).toBe(400);
      
      const data = await resp.json();
      expect(data).toHaveProperty("error");
      expect(data.error).toContain("text is required");
    });

    it("should handle very long text input", async () => {
      const longText = "a".repeat(10000);
      
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: longText }),
      });

      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(data).toHaveProperty("similarities");
      expect(Array.isArray(data.similarities)).toBe(true);
    });

    it("should handle special characters and unicode", async () => {
      const specialText = "🌰 Testing with emojis and unicode: 你好世界! @#$%^&*()";
      
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: specialText }),
      });

      expect(resp.status).toBe(200);
      
      const data = await resp.json();
      expect(data).toHaveProperty("similarities");
      expect(data.query).toBe(specialText);
    });

    it("should handle malformed JSON", async () => {
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "invalid json",
      });

      expect(resp.status).toBe(400);
      
      const data = await resp.json();
      expect(data).toHaveProperty("error");
    });
  });

  describe("🌰 Batch Similarity Search", () => {
    it("should process multiple texts efficiently", async () => {
      const texts = [
        "Blockchain is revolutionary",
        "Cryptocurrency market trends",
        "DeFi protocols and yield farming"
      ];

      const promises = texts.map(text => 
        worker.fetch("/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        })
      );

      const responses = await Promise.all(promises);
      
      responses.forEach(resp => {
        expect(resp.status).toBe(200);
      });

      const results = await Promise.all(
        responses.map(r => r.json())
      );

      results.forEach((result, index) => {
        expect(result.query).toBe(texts[index]);
        expect(Array.isArray(result.similarities)).toBe(true);
      });
    });
  });

  describe("🌰 Rate Limiting and Security", () => {
    it("should handle rapid successive requests", async () => {
      const text = "Testing rate limiting";
      const requests = Array(10).fill(null).map(() =>
        worker.fetch("/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        })
      );

      const responses = await Promise.all(requests);
      
      // All requests should succeed (rate limiting handled by Cloudflare)
      responses.forEach(resp => {
        expect([200, 429]).toContain(resp.status);
      });
    });

    it("should reject non-JSON content type", async () => {
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: "plain text",
      });

      expect(resp.status).toBe(400);
    });

    it("should handle CORS preflight requests", async () => {
      const resp = await worker.fetch("/search", {
        method: "OPTIONS",
        headers: {
          "Origin": "https://example.com",
          "Access-Control-Request-Method": "POST",
          "Access-Control-Request-Headers": "Content-Type",
        },
      });

      expect(resp.status).toBe(200);
      expect(resp.headers.get("Access-Control-Allow-Origin")).toBe("*");
      expect(resp.headers.get("Access-Control-Allow-Methods")).toContain("POST");
    });
  });

  describe("🌰 Response Structure Validation", () => {
    it("should return consistent response format", async () => {
      const resp = await worker.fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "test" }),
      });

      const data = await resp.json();
      
      expect(data).toHaveProperty("similarities");
      expect(data).toHaveProperty("query");
      expect(typeof data.query).toBe("string");
      expect(Array.isArray(data.similarities)).toBe(true);
      
      if (data.similarities.length > 0) {
        const first = data.similarities[0];
        expect(first).toHaveProperty("id");
        expect(first).toHaveProperty("score");
        expect(typeof first.score).toBe("number");
        expect(first.score).toBeGreaterThanOrEqual(0);
        expect(first.score).toBeLessThanOrEqual(1);
      }
    });
  });
});