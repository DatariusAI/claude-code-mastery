// REQ-SHORT-005, NFR-004

/** Base URL for constructing full short URLs */
export const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

/** Length of generated short codes */
export const CODE_LENGTH = 6;

/** Maximum allowed URL length in characters */
export const MAX_URL_LENGTH = 2048;

/** Blocked domains that must be rejected @req REQ-SHORT-005 */
export const BLOCKED_DOMAINS: string[] = [
  'malware.example.com',
  'phishing.example.com',
  'spam.example.com',
];

/** Characters used for short code generation */
export const CODE_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

/** Maximum retries for collision-safe code generation */
export const MAX_CODE_RETRIES = 10;
