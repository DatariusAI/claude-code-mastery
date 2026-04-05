// REQ-SHORT-003, REQ-SHORT-007

import { Hono } from 'hono';
import { findByCode, getAnalytics } from '../lib/store.js';
import type { ErrorResponse, AnalyticsResponse } from '../types.js';

const app = new Hono();

/**
 * GET /analytics/:code — Get analytics for a short URL
 * @req REQ-SHORT-003
 * @req REQ-SHORT-007
 */
app.get('/analytics/:code', (c) => {
  const code = c.req.param('code');
  const record = findByCode(code);

  // REQ-SHORT-003: 404 if not found
  if (!record) {
    return c.json<ErrorResponse>(
      { error: { code: 404, message: 'Short code not found', details: null } },
      404
    );
  }

  // REQ-SHORT-003: Return analytics (works for expired/deleted URLs too)
  const events = getAnalytics(record.id);

  const referrers = [...new Set(events.map((e) => e.referrer).filter((r) => r !== ''))];
  const lastEvent = events.length > 0 ? events[events.length - 1] : null;

  const response: AnalyticsResponse = {
    shortCode: record.shortCode,
    originalUrl: record.originalUrl,
    clickCount: events.length,
    lastAccessedAt: lastEvent ? lastEvent.accessedAt : null,
    referrers,
  };

  return c.json(response, 200);
});

export default app;
