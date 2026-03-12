// 🌰 GitHub webhook signature verification
import { createHmac } from 'crypto';

export function verifyGitHubWebhook(payload, signature, secret) {
  if (!secret) {
    console.warn('🌰 No webhook secret configured');
    return true; // Allow in development
  }
  
  const expectedSignature = 'sha256=' + createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
    
  return crypto.subtle.timingSafeEqual(
    new TextEncoder().encode(signature),
    new TextEncoder().encode(expectedSignature)
  );
}