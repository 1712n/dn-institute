export function parseReviewerAllowlist(raw: string | undefined | null): Set<string> {
  const out = new Set<string>();
  if (!raw) return out;
  const trimmed = raw.trim();
  if (!trimmed) return out;

  // Preferred format (parity with GitHub Actions secret): JSON array of usernames.
  if (trimmed.startsWith("[")) {
    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        for (const item of parsed) {
          if (typeof item === "string" && item.trim()) out.add(item.trim().toLowerCase());
        }
        return out;
      }
    } catch {
      // fall through to delimiter parsing
    }
  }

  // Fallback: newline/comma/space separated.
  for (const part of trimmed.split(/[\n,\s]+/g)) {
    const u = part.trim();
    if (!u) continue;
    out.add(u.toLowerCase());
  }
  return out;
}

