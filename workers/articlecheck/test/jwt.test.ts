import { describe, expect, it } from "vitest";
import { generateKeyPairSync } from "node:crypto";
import { createGitHubAppJwt } from "../common/src/github/app";
import { pemToDerBytes } from "../common/src/pem";

function base64UrlToBytes(b64url: string): Uint8Array<ArrayBuffer> {
  let s = b64url.replace(/-/g, "+").replace(/_/g, "/");
  while (s.length % 4) s += "=";
  const bin = atob(s);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes as Uint8Array<ArrayBuffer>;
}

function base64UrlToJson(b64url: string): any {
  const bytes = base64UrlToBytes(b64url);
  const txt = new TextDecoder().decode(bytes);
  return JSON.parse(txt);
}

describe("createGitHubAppJwt", () => {
  it("creates a verifiable RS256 JWT", async () => {
    const { privateKey, publicKey } = generateKeyPairSync("rsa", {
      modulusLength: 2048,
      publicKeyEncoding: { type: "spki", format: "pem" },
      privateKeyEncoding: { type: "pkcs8", format: "pem" }
    });

    const jwt = await createGitHubAppJwt({ appId: "12345", privateKeyPem: privateKey });
    const [h, p, s] = jwt.split(".");
    expect(h).toBeTruthy();
    expect(p).toBeTruthy();
    expect(s).toBeTruthy();

    const header = base64UrlToJson(h);
    const payload = base64UrlToJson(p);
    expect(header.alg).toBe("RS256");
    expect(payload.iss).toBe("12345");
    expect(typeof payload.iat).toBe("number");
    expect(typeof payload.exp).toBe("number");

    const verifyKey = await crypto.subtle.importKey(
      "spki",
      pemToDerBytes(publicKey),
      { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
      false,
      ["verify"]
    );

    const signingInput = new TextEncoder().encode(`${h}.${p}`) as Uint8Array<ArrayBuffer>;
    const sigBytes = base64UrlToBytes(s);
    const ok = await crypto.subtle.verify({ name: "RSASSA-PKCS1-v1_5" }, verifyKey, sigBytes, signingInput);
    expect(ok).toBe(true);
  });
});

