// 🌰 Unified diff parser — ported from the Python implementation 🌰

import type { DiffFile, DiffSegment } from "./types";

/**
 * 🌰 Parse a unified diff string into structured file/segment objects.
 * Mirrors the logic in tools/python_modules/git.py:parse_diff
 */
export function parseDiff(diff: string): DiffFile[] {
  // 🌰 Split by file boundaries
  const rawFiles = diff.split("diff --git ");
  // Remove the first empty element
  rawFiles.shift();

  const files: DiffFile[] = [];

  for (const rawFile of rawFiles) {
    // 🌰 Split into segments delimited by @@ markers
    const rawSegments = rawFile.split("@@");
    const fileHeader = rawSegments.shift() ?? "";

    const segments: DiffSegment[] = [];
    for (let i = 0; i < rawSegments.length; i += 2) {
      if (i + 1 < rawSegments.length) {
        segments.push({
          header: rawSegments[i],
          body: rawSegments[i + 1],
        });
      }
    }

    files.push({ header: fileHeader, body: segments });
  }

  return files;
}

/**
 * 🌰 Remove leading '+' from diff lines (added lines marker).
 * Mirrors tools/python_modules/llm_utils.py:remove_plus
 */
export function removePlus(text: string): string {
  return text
    .split("\n")
    .map((line) => (line.startsWith("+") ? line.slice(1) : line))
    .join("\n");
}

/**
 * 🌰 Extract the article text from parsed diff files.
 * Takes the first file's header + first segment body and strips diff markers.
 */
export function extractArticleText(files: DiffFile[]): string | null {
  if (files.length === 0) return null;
  const file = files[0];
  if (file.body.length === 0) return null;
  const raw = file.header + file.body[0].body;
  return removePlus(raw);
}
