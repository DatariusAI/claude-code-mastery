// REQ-SHORT-001

import { CODE_LENGTH, CODE_CHARS, MAX_CODE_RETRIES } from '../constants.js';
import { findByCode } from './store.js';
import { randomInt } from 'node:crypto';

/**
 * Generate a collision-safe short code
 * @req REQ-SHORT-001
 * @returns 6-char alphanumeric string
 * @throws Error if unable to generate unique code after MAX_CODE_RETRIES attempts
 */
export function generateCode(): string {
  for (let attempt = 0; attempt < MAX_CODE_RETRIES; attempt++) {
    let code = '';
    for (let i = 0; i < CODE_LENGTH; i++) {
      code += CODE_CHARS[randomInt(0, CODE_CHARS.length)];
    }
    if (!findByCode(code)) {
      return code;
    }
  }
  throw new Error(`Failed to generate unique code after ${MAX_CODE_RETRIES} attempts`);
}
