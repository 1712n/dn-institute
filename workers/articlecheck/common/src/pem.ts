import { base64DecodeToBytes } from "./base64url";

export function normalizePem(pem: string): string {
  // Wrangler secrets often end up with literal "\n" sequences.
  return pem.replace(/\\n/g, "\n").trim();
}

export function pemToDerBytes(pem: string): Uint8Array<ArrayBuffer> {
  const normalized = normalizePem(pem);
  const body = normalized
    .replace(/-----BEGIN [^-]+-----/g, "")
    .replace(/-----END [^-]+-----/g, "")
    .replace(/\s+/g, "");
  return base64DecodeToBytes(body);
}
