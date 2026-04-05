// TESTS: REQ-SHORT-005
import { describe, it, expect } from 'vitest';
import { validateUrl } from '../src/src/lib/validator.js';

// Scenario: SCEN-004, SCEN-009 — URL validation
describe('validateUrl', () => {
  // Scenario: SCEN-001 prerequisite — Valid https URL
  it('should accept a valid https URL', () => {
    const result = validateUrl('https://example.com/path');
    expect(result.valid).toBe(true);
  });

  // Scenario: SCEN-001 prerequisite — Valid http URL
  it('should accept a valid http URL', () => {
    const result = validateUrl('http://example.com/path');
    expect(result.valid).toBe(true);
  });

  // Scenario: SCEN-004 — Missing protocol
  it('should reject a URL without protocol', () => {
    const result = validateUrl('example.com/path');
    expect(result.valid).toBe(false);
    expect(result.reason).toBeDefined();
  });

  // Scenario: SCEN-004 — Empty string
  it('should reject an empty string', () => {
    const result = validateUrl('');
    expect(result.valid).toBe(false);
  });

  // Scenario: SCEN-004 — Blocked domain
  it('should reject a blocked domain', () => {
    const result = validateUrl('https://malware.example.com/bad');
    expect(result.valid).toBe(false);
    expect(result.blocked).toBe(true);
  });

  // Scenario: SCEN-009 — URL exceeding MAX_URL_LENGTH
  it('should reject a URL exceeding 2048 characters', () => {
    const longUrl = 'https://example.com/' + 'a'.repeat(2040);
    const result = validateUrl(longUrl);
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('2048');
  });

  // Additional — ftp scheme
  it('should reject ftp:// scheme', () => {
    const result = validateUrl('ftp://example.com/file');
    expect(result.valid).toBe(false);
    expect(result.reason).toContain('http');
  });
});
