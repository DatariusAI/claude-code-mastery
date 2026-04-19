// TESTS: REQ-SHORT-001, REQ-SHORT-003, REQ-SHORT-005
import { describe, it, expect, beforeEach } from 'vitest';
import app from '../src/src/index.js';

// Reset store between tests by reimporting fresh
beforeEach(async () => {
  const store = await import('../src/src/lib/store.js');
  // Clear maps via module internals - we test through the API
});

// Scenario: SCEN-001 — Successfully shorten a valid URL
describe('POST /shorten', () => {
  it('should return 201 with shortUrl for a valid URL', async () => {
    const res = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/very/long/path' }),
    });
    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body).toHaveProperty('shortUrl');
    expect(body).toHaveProperty('originalUrl', 'https://example.com/very/long/path');
    expect(body).toHaveProperty('shortCode');
    expect(body.shortCode).toMatch(/^[a-zA-Z0-9]{6}$/);
    expect(body).toHaveProperty('createdAt');
  });

  // Scenario: SCEN-001 — POST with expiresAt
  it('should accept and return expiresAt when provided', async () => {
    const futureDate = new Date(Date.now() + 86400000).toISOString();
    const res = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/expiry-test', expiresAt: futureDate }),
    });
    expect(res.status).toBe(201);
    const body = await res.json();
    expect(body.expiresAt).toBe(futureDate);
  });

  // Scenario: SCEN-005 — Reject duplicate URL
  it('should return 409 for a duplicate URL', async () => {
    const url = 'https://example.com/duplicate-test-' + Date.now();
    await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const res = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    expect(res.status).toBe(409);
    const body = await res.json();
    expect(body.error.code).toBe(409);
    expect(body.error.message).toContain('already shortened');
  });

  // Scenario: SCEN-004 — Reject invalid URL (no protocol)
  it('should return 400 for a URL without protocol', async () => {
    const res = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'not-a-valid-url' }),
    });
    expect(res.status).toBe(400);
    const body = await res.json();
    expect(body.error.code).toBe(400);
  });

  // Scenario: SCEN-004 variant — Reject blocked domain
  it('should return 403 for a blocked domain', async () => {
    const res = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://malware.example.com/bad' }),
    });
    expect(res.status).toBe(403);
    const body = await res.json();
    expect(body.error.code).toBe(403);
  });
});
