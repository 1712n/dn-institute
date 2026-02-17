/**
 * Parse a unified diff into structured file objects.
 * Mirrors the Python parse_diff logic from the original bot.
 */

export interface DiffFile {
  header: string;
  segments: Array<{ header: string; body: string }>;
}

export function parseDiff(raw: string): DiffFile[] {
  const rawFiles = raw.split("diff --git ");
  // First element is empty
  rawFiles.shift();

  return rawFiles.map((rawFile) => {
    const parts = rawFile.split("@@");
    const header = parts.shift() ?? "";

    const segments: Array<{ header: string; body: string }> = [];
    for (let i = 0; i < parts.length; i += 2) {
      if (i + 1 < parts.length) {
        segments.push({ header: parts[i], body: parts[i + 1] });
      }
    }

    return { header, segments };
  });
}

/** Remove leading '+' from diff lines (added lines) */
export function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => (line.startsWith("+") ? line.slice(1) : line))
    .join("\n");
}

/** Extract added content from all diff files, filtering to content/ paths only */
export function extractArticleContent(files: DiffFile[]): string[] {
  return files
    .filter((f) => f.header.includes("content/"))
    .map((f) => {
      const allBody = f.segments.map((s) => s.body).join("\n");
      return removePlus(f.header + allBody);
    })
    .filter((text) => text.trim().length > 0);
}
