// TESTS: REQ-SHORT-003
import { describe, it, expect } from 'vitest';
import app from '../src/src/index.js';

// Scenario: SCEN-003 — Retrieve analytics for a short URL
describe('GET /analytics/:code', () => {
  it('should return analytics with clickCount, lastAccessedAt, referrers', async () => {
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/analytics-test-' + Date.now() }),
    });
    const { shortCode } = await createRes.json();

    // Generate a click
    await app.request(`/${shortCode}`, { redirect: 'manual' });

    const res = await app.request(`/analytics/${shortCode}`);
    expect(res.status).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('shortCode', shortCode);
    expect(body).toHaveProperty('clickCount', 1);
    expect(body).toHaveProperty('lastAccessedAt');
    expect(body).toHaveProperty('referrers');
    expect(Array.isArray(body.referrers)).toBe(true);
  });

  // Scenario: SCEN-003 — Click count after 3 redirects
  it('should return clickCount = 3 after 3 redirects', async () => {
    const createRes = await app.request('/shorten', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://example.com/three-clicks-' + Date.now() }),
    });
    const { shortCode } = await createRes.json();

    await app.request(`/${shortCode}`, { redirect: 'manual' });
    await app.request(`/${shortCode}`, { redirect: 'manual' });
    await app.request(`/${shortCode}`, { redirect: 'manual' });

    const res = await app.request(`/analytics/${shortCode}`);
    const body = await res.json();
    expect(body.clickCount).toBe(3);
  });

  // Scenario: SCEN-008 variant — Analytics for unknown code returns 404
  it('should return 404 for analytics of non-existent code', async () => {
    const res = await app.request('/analytics/zzz999');
    expect(res.status).toBe(404);
    const body = await res.json();
    expect(body.error.code).toBe(404);
  });
});
