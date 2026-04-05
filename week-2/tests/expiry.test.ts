// TESTS: REQ-SHORT-004
import { describe, it, expect } from 'vitest';
import app from '../src/src/index.js';

// Scenario: SCEN-006 — URL expiry behavior
describe('URL Expiry', () => {
  // Scenario: SCEN-001 — URL with no expiry is always active
  it('should redirect indefinitely when no expiresAt is set', async () => {
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/no-expiry-' + Date.now() }),
    });
    const { shortCode, expiresAt } = await createRes.json();
    expect(expiresAt).toBeNull();

    const res = await app.request(`/${shortCode}`, { redirect: 'manual' });
    expect(res.status).toBe(301);
  });

  // Scenario: SCEN-006 — URL with future expiresAt is active
  it('should redirect when expiresAt is in the future', async () => {
    const futureDate = new Date(Date.now() + 86400000).toISOString();
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/future-expiry-' + Date.now(), expiresAt: futureDate }),
    });
    const { shortCode } = await createRes.json();

    const res = await app.request(`/${shortCode}`, { redirect: 'manual' });
    expect(res.status).toBe(301);
  });

  // Scenario: SCEN-006 — Expired URL returns 410
  it('should return 410 for an expired URL', async () => {
    const futureDate = new Date(Date.now() + 86400000).toISOString();
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/will-expire-' + Date.now(), expiresAt: futureDate }),
    });
    const { shortCode } = await createRes.json();

    // Manipulate store to expire the URL
    const store = await import('../src/src/lib/store.js');
    const record = store.findByCode(shortCode);
    if (record) record.expiresAt = new Date(Date.now() - 1000).toISOString();

    const res = await app.request(`/${shortCode}`);
    expect(res.status).toBe(410);
  });

  // Scenario: SCEN-006 — Analytics not incremented after expiry
  it('should not record analytics for expired URL access', async () => {
    const futureDate = new Date(Date.now() + 86400000).toISOString();
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/analytics-expiry-' + Date.now(), expiresAt: futureDate }),
    });
    const { shortCode } = await createRes.json();

    // One valid click
    await app.request(`/${shortCode}`, { redirect: 'manual' });

    // Expire it
    const store = await import('../src/src/lib/store.js');
    const record = store.findByCode(shortCode);
    if (record) record.expiresAt = new Date(Date.now() - 1000).toISOString();

    // Attempt access (should get 410, no analytics recorded)
    await app.request(`/${shortCode}`);

    const analyticsRes = await app.request(`/analytics/${shortCode}`);
    const body = await analyticsRes.json();
    expect(body.clickCount).toBe(1); // Only the first valid click
  });
});
