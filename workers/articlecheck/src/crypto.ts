/**
 * 🌰 Webhook signature verification using Web Crypto API.
 * Verifies GitHub's X-Hub-Signature-256 header (HMAC-SHA256).
 */

/**
 * Verify that the webhook payload was signed by GitHub. 🌰
 */
export async function verifyWebhookSignature(
	payload: string,
	signatureHeader: string,
	secret: string,
): Promise<boolean> {
	const encoder = new TextEncoder();

	const key = await crypto.subtle.importKey(
		'raw',
		encoder.encode(secret),
		{ name: 'HMAC', hash: 'SHA-256' },
		false,
		['sign'],
	);

	const signatureBytes = await crypto.subtle.sign('HMAC', key, encoder.encode(payload));
	const computed = 'sha256=' + bufferToHex(signatureBytes);

	// Constant-time comparison to prevent timing attacks 🌰
	return timingSafeEqual(computed, signatureHeader);
}

function bufferToHex(buffer: ArrayBuffer): string {
	return [...new Uint8Array(buffer)].map(b => b.toString(16).padStart(2, '0')).join('');
}

function timingSafeEqual(a: string, b: string): boolean {
	if (a.length !== b.length) return false;
	let result = 0;
	for (let i = 0; i < a.length; i++) {
		result |= a.charCodeAt(i) ^ b.charCodeAt(i);
	}
	return result === 0;
}
