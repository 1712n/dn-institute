export interface SearchResult {
  title: string;
  url: string;
  description: string;
}

export class BraveSearchClient {
  private apiKey: string;
  private baseUrl = "https://api.search.brave.com/res/v1/web/search";

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async search(query: string, count: number = 3): Promise<SearchResult[]> {
    const url = new URL(this.baseUrl);
    url.searchParams.set("q", query);
    url.searchParams.set("count", count.toString());

    const response = await fetch(url.toString(), {
      headers: {
        "X-Subscription-Token": this.apiKey,
        "Accept": "application/json",
      },
    });

    if (!response.ok) {
      console.error(`Brave Search failed: ${response.status} ${response.statusText}`);
      return [];
    }

    const data: any = await response.json();
    if (!data.web || !data.web.results) return [];

    return data.web.results.map((r: any) => ({
      title: r.title,
      url: r.url,
      description: r.description,
    }));
  }
}
