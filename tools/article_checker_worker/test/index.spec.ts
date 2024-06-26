import { SELF } from 'cloudflare:test';
import { describe, it, expect } from 'vitest';

export interface GitHubPayload {
    action: string;
    comment: { body: string };
    pull_request: { url: string };
  }

describe('Webhook Processor', () => {
  it('should process valid POST requests with /articlecheck command', async () => {
    const mockPayload: GitHubPayload = {
      action: 'created',
      comment: { body: '/articlecheck' },
      pull_request: { url: 'https://api.github.com/repos/owner/repo/pulls/1' },
    };

    const response = await SELF.fetch('https://example.com', {
      method: 'POST',
      body: JSON.stringify(mockPayload),
      headers: { 'Content-Type': 'application/json' },
    });

    expect(response.status).toBe(200);
    expect(await response.text()).toBe('Payload sent to queue for processing');
  });

  it('should reject non-POST requests', async () => {
    const response = await SELF.fetch('https://example.com');
    expect(response.status).toBe(405);
    expect(await response.text()).toBe('Method not allowed');
  });

  it('should ignore comments without /articlecheck command', async () => {
    const mockPayload: GitHubPayload = {
      action: 'created',
      comment: { body: 'Just a regular comment' },
      pull_request: { url: 'https://api.github.com/repos/owner/repo/pulls/1' },
    };

    const response = await SELF.fetch('https://example.com', {
      method: 'POST',
      body: JSON.stringify(mockPayload),
      headers: { 'Content-Type': 'application/json' },
    });

    expect(response.status).toBe(200);
    expect(await response.text()).toBe('No action taken');
  });

  it('should ignore actions other than "created"', async () => {
    const mockPayload: GitHubPayload = {
      action: 'deleted', 
      comment: { body: '/articlecheck' },
      pull_request: { url: 'https://api.github.com/repos/owner/repo/pulls/1' },
    };

    const response = await SELF.fetch('https://example.com', {
      method: 'POST',
      body: JSON.stringify(mockPayload),
      headers: { 'Content-Type': 'application/json' },
    });

    expect(response.status).toBe(200);
    expect(await response.text()).toBe('No action taken');
  });

  it('should handle processing errors', async () => {
    const response = await SELF.fetch('https://example.com', {
      method: 'POST',
      body: 'invalid JSON',
      headers: { 'Content-Type': 'application/json' },
    });

    expect(response.status).toBe(500);
    expect(await response.text()).toContain('Error processing request');
  });
});