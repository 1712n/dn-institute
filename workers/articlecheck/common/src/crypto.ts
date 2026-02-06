import { timingSafeEqual, toLowerAscii } from "./strings";

const encoder = new TextEncoder();

function hexEncode(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  let out = "";
  for (const b of bytes) out += b.toString(16).padStart(2, "0");
  return out;
}

export async function verifyHmacSha256HexSignature(opts: {
  secret: string;
  payload: ArrayBuffer;
  expectedHexDigest: string;
}): Promise<boolean> {
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(opts.secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const mac = await crypto.subtle.sign("HMAC", key, opts.payload);
  const ours = toLowerAscii(hexEncode(mac));
  const theirs = toLowerAscii(opts.expectedHexDigest);
  return timingSafeEqual(ours, theirs);
}

