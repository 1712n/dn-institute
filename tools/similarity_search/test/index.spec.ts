import { SELF } from "cloudflare:test";
import { describe, it, expect } from "vitest";

import "../src/index";

describe("Authentication", () => {
  it("should return 401 Unauthorized when API key is missing", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    });

    expect(response.status).toBe(401);
    expect(await response.text()).toBe("Unauthorized");
  });

  it("should return 401 Unauthorized when API key is invalid", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "invalid-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    });

    expect(response.status).toBe(401);
    expect(await response.text()).toBe("Unauthorized");
  });
});

describe("Integration Tests for Similarity Search API", () => {
  it("should return similarity score when sending valid data", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "valid-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    });

    expect(response.status).toBe(200);
    const responseBody = await response.json();
    expect(responseBody).toHaveProperty("similarity_score");
  });

  it("should return 400 Bad Request when sending invalid JSON format", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "valid-api-key"
      },
      body: "invalid data"
    });

    expect(response.status).toBe(400);
  });

  it("should return 400 Bad Request when sending incomplete data", async () => {
    const response = await SELF.fetch("https://example.com/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "valid-api-key"
      },
      body: JSON.stringify({
        text: "Sample text"
      })
    });

    expect(response.status).toBe(400);
  });

  it("should return 404 Not Found for non-existent route", async () => {
    const response = await SELF.fetch("https://example.com/non-existent", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": "valid-api-key"
      },
      body: JSON.stringify({
        text: "Sample text",
        namespace: "test-namespace"
      })
    });

    expect(response.status).toBe(404);
  });
});
