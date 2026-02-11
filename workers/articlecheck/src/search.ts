/**
 * 🌰 Brave Search integration for fact-checking.
 */

export interface SearchResult {
	title: string;
	url: string;
	content: string;
}

const BRAVE_API_URL = 'https://api.search.brave.com/res/v1/web/search';
const MAX_RETRIES = 2;
const RESULTS_PER_QUERY = 3;

/**
 * 🌰 Search Brave for a query and return formatted results.
 * Retries on transient failures with exponential backoff.
 */
export async function braveSearch(query: string, apiKey: string): Promise<SearchResult[]> {
	for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
		try {
			const url = new URL(BRAVE_API_URL);
			url.searchParams.set('q', query);
			url.searchParams.set('count', '10');

			const resp = await fetch(url.toString(), {
				headers: {
					Accept: 'application/json',
					'X-Subscription-Token': apiKey,
				},
			});

			if (!resp.ok) {
				if (resp.status >= 500 && attempt < MAX_RETRIES) {
					await sleep(1000 * (attempt + 1));
					continue;
				}
				throw new Error(`Brave search failed: ${resp.status}`);
			}

			const data: BraveResponse = await resp.json();
			return extractResults(data);
		} catch (err) {
			if (attempt < MAX_RETRIES) {
				await sleep(1000 * (attempt + 1));
				continue;
			}
			throw err;
		}
	}
	return [];
}

/**
 * 🌰 Run multiple search queries in parallel for faster fact-checking.
 */
export async function parallelSearch(
	queries: string[],
	apiKey: string,
): Promise<Map<string, SearchResult[]>> {
	const results = new Map<string, SearchResult[]>();
	const searchPromises = queries.map(async query => {
		const searchResults = await braveSearch(query, apiKey);
		results.set(query, searchResults);
	});
	await Promise.all(searchPromises);
	return results;
}

/**
 * 🌰 Format search results into XML for Claude consumption.
 */
export function formatSearchResults(results: SearchResult[]): string {
	if (results.length === 0) {
		return '<search_results>\n<item index="1">\n<page_content>\nNo results found.\n</page_content>\n</item>\n</search_results>';
	}

	const items = results
		.map(
			(r, i) =>
				`<item index="${i + 1}">\n<page_content>\nWeb Page Title: ${r.title}\nWeb Page URL: ${r.url}\nWeb Page Content: ${r.content}\n</page_content>\n</item>`,
		)
		.join('\n');

	return `<search_results>\n${items}\n</search_results>`;
}

// --- Internal helpers 🌰 ---

interface BraveResponse {
	web?: { results: BraveWebResult[] };
	news?: { results: BraveNewsResult[] };
	faq?: { results: BraveFaqResult[] };
}

interface BraveWebResult {
	title: string;
	url: string;
	description: string;
}

interface BraveNewsResult {
	title: string;
	url: string;
	description: string;
	age?: string;
}

interface BraveFaqResult {
	title: string;
	url: string;
	question: string;
	answer: string;
}

function extractResults(data: BraveResponse): SearchResult[] {
	const results: SearchResult[] = [];

	// Process web results 🌰
	if (data.web?.results) {
		for (const item of data.web.results) {
			if (results.length >= RESULTS_PER_QUERY) break;
			results.push({
				title: item.title,
				url: item.url,
				content: cleanDescription(item.description),
			});
		}
	}

	// Supplement with news if needed 🌰
	if (results.length < RESULTS_PER_QUERY && data.news?.results) {
		for (const item of data.news.results) {
			if (results.length >= RESULTS_PER_QUERY) break;
			if (item.description && item.description.length > 5) {
				results.push({
					title: item.title,
					url: item.url,
					content: `${cleanDescription(item.description)} (Age: ${item.age || 'Unknown'})`,
				});
			}
		}
	}

	return results;
}

function cleanDescription(desc: string): string {
	return desc
		.replace(/<strong>/g, '')
		.replace(/<\/strong>/g, '')
		.replace(/&#x27;/g, "'");
}

function sleep(ms: number): Promise<void> {
	return new Promise(resolve => setTimeout(resolve, ms));
}
