import { base64UrlEncodeString, base64UrlEncodeBytes } from "../base64url";
import { pemToDerBytes } from "../pem";

export type GitHubAppConfig = {
  appId: string;
  privateKeyPem: string;
};

type CachedToken = { token: string; expiresAtMs: number };

// Best-effort in-memory cache per isolate. KV not necessary for short-lived installation tokens.
const installationTokenCache = new Map<number, CachedToken>();

function nowSeconds(): number {
  return Math.floor(Date.now() / 1000);
}

async function importGitHubAppPrivateKey(privateKeyPem: string): Promise<CryptoKey> {
  const pkcs8 = pemToDerBytes(privateKeyPem);
  return crypto.subtle.importKey(
    "pkcs8",
    pkcs8,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"]
  );
}

async function signRs256(
  privateKey: CryptoKey,
  data: Uint8Array<ArrayBuffer>
): Promise<Uint8Array<ArrayBuffer>> {
  const sig = await crypto.subtle.sign({ name: "RSASSA-PKCS1-v1_5" }, privateKey, data);
  return new Uint8Array(sig) as Uint8Array<ArrayBuffer>;
}

export async function createGitHubAppJwt(opts: GitHubAppConfig): Promise<string> {
  const iat = nowSeconds() - 5;
  const exp = iat + 9 * 60; // <= 10 minutes per GitHub docs; keep a buffer.
  const header = base64UrlEncodeString(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const payload = base64UrlEncodeString(JSON.stringify({ iat, exp, iss: opts.appId }));
  const signingInput = `${header}.${payload}`;
  const key = await importGitHubAppPrivateKey(opts.privateKeyPem);
  const sigBytes = await signRs256(key, new TextEncoder().encode(signingInput) as Uint8Array<ArrayBuffer>);
  const sig = base64UrlEncodeBytes(sigBytes);
  return `${signingInput}.${sig}`;
}

export async function getInstallationAccessToken(opts: {
  installationId: number;
  app: GitHubAppConfig;
}): Promise<string> {
  const cached = installationTokenCache.get(opts.installationId);
  if (cached && cached.expiresAtMs - Date.now() > 60_000) return cached.token; // 60s safety window

  const jwt = await createGitHubAppJwt(opts.app);
  const resp = await fetch(`https://api.github.com/app/installations/${opts.installationId}/access_tokens`, {
    method: "POST",
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${jwt}`,
      "User-Agent": "dn-institute-articlecheck-worker",
      "X-GitHub-Api-Version": "2022-11-28"
    }
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`github_installation_token_failed status=${resp.status} body=${text.slice(0, 600)}`);
  }
  const data = (await resp.json()) as { token: string; expires_at: string };
  const expiresAtMs = Date.parse(data.expires_at);
  installationTokenCache.set(opts.installationId, { token: data.token, expiresAtMs });
  return data.token;
}
