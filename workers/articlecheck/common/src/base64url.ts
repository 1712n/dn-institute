const encoder = new TextEncoder();

export function base64UrlEncodeBytes(bytes: Uint8Array): string {
  let str = "";
  for (const b of bytes) str += String.fromCharCode(b);
  // btoa expects binary string (Latin-1).
  const base64 = btoa(str);
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

export function base64UrlEncodeString(s: string): string {
  return base64UrlEncodeBytes(encoder.encode(s));
}

export function base64DecodeToBytes(base64: string): Uint8Array<ArrayBuffer> {
  const bin = atob(base64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  // The underlying buffer is always an ArrayBuffer in this environment.
  return bytes as Uint8Array<ArrayBuffer>;
}
