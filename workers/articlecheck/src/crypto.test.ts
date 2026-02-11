/**
 * 🌰 Tests for webhook signature verification.
 */
import { describe, it, expect } from 'vitest';
import { verifyWebhookSignature } from './crypto';

describe('🌰 verifyWebhookSignature', () => {
	const secret = 'test-secret-key';

	it('should verify a valid signature', async () => {
		// Pre-computed HMAC-SHA256 of "hello" with secret "test-secret-key"
		const payload = 'hello';
		// Generate the expected signature
		const encoder = new TextEncoder();
		const key = await crypto.subtle.importKey(
			'raw',
			encoder.encode(secret),
			{ name: 'HMAC', hash: 'SHA-256' },
			false,
			['sign'],
		);
		const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(payload));
		const hex = [...new Uint8Array(sig)].map(b => b.toString(16).padStart(2, '0')).join('');
		const signature = `sha256=${hex}`;

		const result = await verifyWebhookSignature(payload, signature, secret);
		expect(result).toBe(true);
	});

	it('should reject an invalid signature', async () => {
		const result = await verifyWebhookSignature('hello', 'sha256=invalid', secret);
		expect(result).toBe(false);
	});

	it('should reject a signature with wrong length', async () => {
		const result = await verifyWebhookSignature('hello', 'sha256=abc', secret);
		expect(result).toBe(false);
	});
});
