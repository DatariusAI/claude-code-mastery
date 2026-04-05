// REQ-SHORT-005

import { MAX_URL_LENGTH, BLOCKED_DOMAINS } from '../constants.js';

interface ValidationResult {
  valid: boolean;
  reason?: string;
  blocked?: boolean;
}

/**
 * Validate a URL for shortening
 * @req REQ-SHORT-005
 * @returns validation result with reason on failure, blocked flag for domain blocklist
 */
export function validateUrl(url: string): ValidationResult {
  if (!url || typeof url !== 'string') {
    return { valid: false, reason: 'URL is required and must be a string' };
  }

  if (url.length > MAX_URL_LENGTH) {
    return { valid: false, reason: `URL exceeds maximum length of ${MAX_URL_LENGTH} characters` };
  }

  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return { valid: false, reason: 'Invalid URL format' };
  }

  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    return { valid: false, reason: 'URL must use http:// or https:// scheme' };
  }

  const hostname = parsed.hostname.toLowerCase();
  if (BLOCKED_DOMAINS.some((domain) => hostname === domain || hostname.endsWith('.' + domain))) {
    return { valid: false, reason: 'URL domain is blocked', blocked: true };
  }

  return { valid: true };
}
