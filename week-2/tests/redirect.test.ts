// TESTS: REQ-SHORT-002, REQ-SHORT-004
import { describe, it, expect } from 'vitest';
import app from '../src/src/index.js';

// Scenario: SCEN-002 — Redirect via short code
describe('GET /:code', () => {
  it('should return 301 redirect for a valid active code', async () => {
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/redirect-test-' + Date.now() }),
    });
    const { shortCode } = await createRes.json();

    const res = await app.request(`/${shortCode}`, { redirect: 'manual' });
    expect(res.status).toBe(301);
    expect(res.headers.get('location')).toContain('https://example.com/redirect-test');
  });

  // Scenario: SCEN-008 — Unknown code returns 404
  it('should return 404 for a non-existent code', async () => {
    const res = await app.request('/zzz999');
    expect(res.status).toBe(404);
    const body = await res.json();
    expect(body.error.code).toBe(404);
  });

  // Scenario: SCEN-006 — Expired code returns 410
  it('should return 410 for an expired URL', async () => {
    const pastDate = new Date(Date.now() - 1000).toISOString();
    // We need to create a URL that is already expired
    // Since we can't POST with a past expiresAt (validation rejects it),
    // we create with future date then manipulate the store
    const futureDate = new Date(Date.now() + 86400000).toISOString();
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/expiry-redirect-' + Date.now(), expiresAt: futureDate }),
    });
    const { shortCode } = await createRes.json();

    // Directly manipulate store to set expiresAt in the past
    const store = await import('../src/src/lib/store.js');
    const record = store.findByCode(shortCode);
    if (record) record.expiresAt = pastDate;

    const res = await app.request(`/${shortCode}`);
    expect(res.status).toBe(410);
    const body = await res.json();
    expect(body.error.message).toContain('expired');
  });

  // Scenario: SCEN-002 — Click count increments on redirect
  it('should increment click count on successive redirects', async () => {
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/click-count-' + Date.now() }),
    });
    const { shortCode } = await createRes.json();

    await app.request(`/${shortCode}`, { redirect: 'manual' });
    await app.request(`/${shortCode}`, { redirect: 'manual' });

    const analyticsRes = await app.request(`/analytics/${shortCode}`);
    const body = await analyticsRes.json();
    expect(body.clickCount).toBe(2);
  });
});
