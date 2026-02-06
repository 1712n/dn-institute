export function extractAllBetweenTags(tag: string, input: string): string[] {
  const re = new RegExp(`<${tag}\\s?>(.+?)</${tag}\\s?>`, "gs");
  const out: string[] = [];
  for (const m of input.matchAll(re)) out.push(m[1]?.trim() ?? "");
  return out.filter(Boolean);
}

export function extractLastBetweenTags(tag: string, input: string): string | null {
  const all = extractAllBetweenTags(tag, input);
  return all.length ? all[all.length - 1] : null;
}

