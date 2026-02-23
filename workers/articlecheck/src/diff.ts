/**
 * Parse a unified diff to extract added content from article files.
 *
 * Filters to only `content/` markdown files (the crypto attack wiki articles),
 * strips diff metadata, and returns clean text for each changed file.
 */
export interface ParsedFile {
  filename: string
  content: string
}

/**
 * Parse a unified diff string into per-file added content.
 * Only includes files under `content/` matching `*.md`.
 */
export function parseDiff(diff: string): ParsedFile[] {
  const files: ParsedFile[] = []
  const fileSections = diff.split("diff --git ")

  for (const section of fileSections) {
    if (!section.trim()) continue

    // Extract filename from the diff header: "a/path b/path"
    const headerMatch = section.match(/^a\/(.+?)\s+b\/(.+?)$/m)
    if (!headerMatch) continue

    const filename = headerMatch[2] ?? ""

    // Only process markdown files in the content directory
    if (!filename.startsWith("content/") || !filename.endsWith(".md")) {
      continue
    }

    // Extract added lines (lines starting with +, excluding +++ header)
    const lines = section.split("\n")
    const addedLines: string[] = []

    for (const line of lines) {
      if (line.startsWith("+++")) continue
      if (line.startsWith("+")) {
        addedLines.push(line.slice(1))
      }
    }

    if (addedLines.length > 0) {
      files.push({
        filename,
        content: addedLines.join("\n")
      })
    }
  }

  return files
}

/**
 * Remove leading '+' from diff lines (for compatibility with the
 * original Python `remove_plus` utility).
 */
export function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => (line.startsWith("+") ? line.slice(1) : line))
    .join("\n")
}
