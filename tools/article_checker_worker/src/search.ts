interface WebSearchResponse {
    error?: boolean;
    statusCode?: number;
    message?: string;
    web?: { results: RawSearchResult[] };
}

interface RawSearchResult {
    title: string;
    url: string;
    description: string;
}

export async function webSearch(params: any, BRAVE_API_KEY: string, SEARCH_ENDPOINT: string): Promise<WebSearchResponse> {
    const apiKey = BRAVE_API_KEY;
    const url = new URL(SEARCH_ENDPOINT);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    const headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": apiKey
    };

    const response = await fetch(url.toString(), { headers });

    if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.statusText}`);
    }

    return await response.json() as WebSearchResponse;
}

export function formatResultsFull(rawSearchResults: RawSearchResult[]): string {
    let result = '<search_results>\n';
    rawSearchResults.forEach((rawSearchResult, index) => {
        result += `<item index="${index + 1}">\n`;
        result += `<page_content>\n`;
        result += `Web Page Title: ${rawSearchResult.title}\n`;
        result += `Web Page URL: ${rawSearchResult.url}\n`;
        result += `Web Page Summary: <summary>`;
        result += `- ${rawSearchResult.description.replace(/<strong>/g, '').replace(/<\/strong>/g, '')}\n`;
        result += `</summary>\n`;
        result += `</page_content>\n`;
        result += `</item>\n`;
    });
    result += '</search_results>';
    return result;
}