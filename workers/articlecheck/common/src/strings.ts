export function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i++) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}

export function toLowerAscii(s: string): string {
  // GitHub signature is hex; ASCII lowercasing is sufficient.
  return s.replace(/[A-Z]/g, (c) => String.fromCharCode(c.charCodeAt(0) | 32));
}

