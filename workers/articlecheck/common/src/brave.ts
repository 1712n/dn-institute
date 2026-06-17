export type BraveWebResult = {
  title: string;
  url: string;
  description: string;
};

export async function braveSearchWeb(opts: {
  apiKey: string;
  query: string;
  count: number;
}): Promise<BraveWebResult[]> {
  const url = new URL("https://api.search.brave.com/res/v1/web/search");
  url.searchParams.set("q", opts.query);
  url.searchParams.set("count", String(Math.min(Math.max(opts.count, 1), 20)));

  const resp = await fetch(url.toString(), {
    headers: {
      Accept: "application/json",
      "X-Subscription-Token": opts.apiKey
    }
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`brave_search_failed status=${resp.status} body=${text.slice(0, 600)}`);
  }
  const data = (await resp.json()) as any;
  const web = data?.web?.results;
  if (!Array.isArray(web)) return [];
  return web
    .map((r: any) => ({
      title: typeof r?.title === "string" ? r.title : "",
      url: typeof r?.url === "string" ? r.url : "",
      description: typeof r?.description === "string" ? r.description : ""
    }))
    .filter((r: BraveWebResult) => !!r.url)
    .slice(0, opts.count);
}

export function formatBraveResults(results: BraveWebResult[]): string {
  const items = results.map((r, i) => {
    const content = [
      `Web Page Title: ${r.title || "Unknown"}`,
      `Web Page URL: ${r.url}`,
      r.description ? `Web Page Description: ${r.description.replaceAll("<strong>", "").replaceAll("</strong>", "")}` : ""
    ]
      .filter(Boolean)
      .join("\n");
    return `<item index="${i + 1}">\n<page_content>\n${content}\n</page_content>\n</item>`;
  });
  return `<search_results>\n${items.join("\n")}\n</search_results>`;
}

