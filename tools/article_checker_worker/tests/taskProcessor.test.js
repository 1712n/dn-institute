import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TaskProcessor } from '../src/taskProcessor.js';

describe('TaskProcessor', () => {
  let state;
  let env;

  beforeEach(() => {
    state = {
      storage: {
        get: vi.fn(),
        put: vi.fn(),
        setAlarm: vi.fn(),
        delete: vi.fn(),
      },
    };
    env = {
      TOKEN_GITHUB: 'test-github-token',
      OPENAI_API_KEY: 'test-openai-api-key',
      LLM_ENDPOINT: 'test-llm-endpoint',
      LLM_MODEL: 'test-llm-model',
      checkerPrompts: {
        get: vi.fn(),
      },
      BRAVE_API_KEY: 'test-brave-api-key',
      SEARCH_ENDPOINT: 'test-search-endpoint',
    };
  });

  it('should schedule processing for a new event', async () => {
    const taskProcessor = new TaskProcessor(state, env);

    const request = new Request('http://localhost/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-GitHub-Delivery': 'test-event-id' },
      body: JSON.stringify({ payload: 'test-payload' }),
    });

    state.storage.get.mockResolvedValueOnce(null); // No existing event
    state.storage.put.mockResolvedValueOnce();
    state.storage.setAlarm.mockResolvedValueOnce();

    const response = await taskProcessor.fetch(request);

    expect(response.status).toBe(200);
    expect(await response.text()).toBe('Processing scheduled');
    expect(state.storage.get).toHaveBeenCalledWith('test-event-id');
    expect(state.storage.put).toHaveBeenCalledWith('payload', 'test-payload');
    expect(state.storage.put).toHaveBeenCalledWith('test-event-id', true);
    expect(state.storage.setAlarm).toHaveBeenCalledWith(expect.any(Number));
  });

  it('should skip processing for a duplicate event', async () => {
    const taskProcessor = new TaskProcessor(state, env);

    const request = new Request('http://localhost/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-GitHub-Delivery': 'test-event-id' },
      body: JSON.stringify({ payload: 'test-payload' }),
    });

    state.storage.get.mockResolvedValueOnce(true); // Existing event

    const response = await taskProcessor.fetch(request);

    expect(response.status).toBe(200);
    expect(await response.text()).toBe('Processing scheduled');
    expect(state.storage.get).toHaveBeenCalledWith('test-event-id');
    expect(state.storage.put).not.toHaveBeenCalled();
    expect(state.storage.setAlarm).not.toHaveBeenCalled();
  });
});