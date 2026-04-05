// REQ-SHORT-002, REQ-SHORT-003, REQ-SHORT-004, REQ-SHORT-007

import { Hono } from 'hono';
import { findByCode, recordAnalytics } from '../lib/store.js';
import type { ErrorResponse, AnalyticsEvent } from '../types.js';
import { randomUUID, createHash } from 'node:crypto';

const app = new Hono();

/**
 * GET /:code — Redirect to original URL
 * @req REQ-SHORT-002
 * @req REQ-SHORT-003
 * @req REQ-SHORT-004
 * @req REQ-SHORT-007
 */
app.get('/:code', (c) => {
  const code = c.req.param('code');
  const record = findByCode(code);

  // REQ-SHORT-002: 404 if not found
  if (!record) {
    return c.json<ErrorResponse>(
      { error: { code: 404, message: 'Short code not found', details: null } },
      404
    );
  }

  // REQ-SHORT-006: 410 if deleted
  if (!record.isActive) {
    return c.json<ErrorResponse>(
      { error: { code: 410, message: 'URL has been deleted', details: null } },
      410
    );
  }

  // REQ-SHORT-004: 410 if expired
  if (record.expiresAt && new Date(record.expiresAt).getTime() <= Date.now()) {
    return c.json<ErrorResponse>(
      { error: { code: 410, message: 'URL has expired', details: null } },
      410
    );
  }

  // REQ-SHORT-003: Record analytics event
  const referrer = c.req.header('referer') || '';
  const clientIp = c.req.header('x-forwarded-for') || c.req.header('x-real-ip') || '0.0.0.0';
  const ipHash = createHash('sha256').update(clientIp).digest('hex');

  const event: AnalyticsEvent = {
    id: randomUUID(),
    urlId: record.id,
    accessedAt: new Date().toISOString(),
    referrer,
    ipHash,
  };

  recordAnalytics(event);

  // REQ-SHORT-002: 301 redirect
  return c.redirect(record.originalUrl, 301);
});

export default app;
