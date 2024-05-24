import { expect, test, vi } from 'vitest';
import { processStatements } from '../../worker-article-rag/src/worker.js'; 
import { webSearch, formatResultsFull } from '../../worker-article-rag/src/search.js';

global.BRAVE_API_KEY = 'fake-brave-api-key';
global.SEARCH_ENDPOINT = 'https://api.search.brave.com/api/search';

vi.mock('../src/search.js', () => ({
  webSearch: vi.fn(),
  formatResultsFull: vi.fn(),
}));

test('processStatements handles web search and formatting correctly', async () => {
  const retrieveAnswer = [
    { q: "Do penguins have the ability to fly over 100 miles like other birds?", count: 3 },
    { q: "Does water boil at 100 degrees Celsius at sea level?", count: 3 }
  ];

  const mockSearchResults = {
    web: {
      results: [
        {
          title: "Penguins can't fly",
          url: "https://example.com/penguins",
          description: "Penguins are birds that can't fly over 100 miles."
        },
        {
          title: "Water boiling point",
          url: "https://example.com/water-boiling",
          description: "Water boils at 100 degrees Celsius at sea level."
        }
      ]
    }
  };

  webSearch.mockResolvedValue(mockSearchResults);
  formatResultsFull.mockReturnValue('<search_results>Mocked formatted results</search_results>');

  const completions = await processStatements(retrieveAnswer, { BRAVE_API_KEY, SEARCH_ENDPOINT });
  expect(completions).toContain('Mocked formatted results');
});