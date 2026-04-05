// REQ-SHORT-001, REQ-SHORT-004, REQ-SHORT-005, REQ-SHORT-007

import { Hono } from 'hono';
import { validateUrl } from '../lib/validator.js';
import { generateCode } from '../lib/shortener.js';
import { save, findByOriginal } from '../lib/store.js';
import { BASE_URL } from '../constants.js';
import type { ShortenRequest, ShortenResponse, ErrorResponse, UrlRecord } from '../types.js';
import { randomUUID } from 'node:crypto';

const app = new Hono();

/**
 * POST /shorten — Create a shortened URL
 * @req REQ-SHORT-001
 * @req REQ-SHORT-004
 * @req REQ-SHORT-005
 * @req REQ-SHORT-007
 */
app.post('/shorten', async (c) => {
  // REQ-SHORT-007: Validate Content-Type
  const contentType = c.req.header('content-type');
  if (!contentType || !contentType.includes('application/json')) {
    return c.json<ErrorResponse>(
      { error: { code: 400, message: 'Content-Type must be application/json', details: null } },
      400
    );
  }

  let body: ShortenRequest;
  try {
    body = await c.req.json<ShortenRequest>();
  } catch {
    return c.json<ErrorResponse>(
      { error: { code: 400, message: 'Invalid JSON body', details: null } },
      400
    );
  }

  if (!body.url || typeof body.url !== 'string') {
    return c.json<ErrorResponse>(
      { error: { code: 400, message: 'Missing required field: url', details: null } },
      400
    );
  }

  // REQ-SHORT-005: Validate URL format, length, scheme, blocklist
  const validation = validateUrl(body.url);
  if (!validation.valid) {
    // REQ-SHORT-005: Blocked domains return 403 per spec
    if (validation.blocked) {
      return c.json<ErrorResponse>(
        { error: { code: 403, message: 'URL domain is blocked', details: validation.reason ?? null } },
        403
      );
    }
    return c.json<ErrorResponse>(
      { error: { code: 400, message: 'Invalid URL format', details: validation.reason ?? null } },
      400
    );
  }

  // REQ-SHORT-005: Check for duplicate
  const existing = findByOriginal(body.url);
  if (existing) {
    return c.json<ErrorResponse>(
      { error: { code: 409, message: 'URL already shortened', details: `${BASE_URL}/${existing.shortCode}` } },
      409
    );
  }

  // REQ-SHORT-004: Validate expiresAt if provided
  if (body.expiresAt !== undefined) {
    if (typeof body.expiresAt !== 'string') {
      return c.json<ErrorResponse>(
        { error: { code: 400, message: 'expiresAt must be a string', details: 'Expected ISO 8601 datetime string' } },
        400
      );
    }
    const expiryDate = new Date(body.expiresAt);
    if (isNaN(expiryDate.getTime())) {
      return c.json<ErrorResponse>(
        { error: { code: 400, message: 'Invalid expiresAt format', details: 'Must be a valid ISO 8601 datetime' } },
        400
      );
    }
    if (expiryDate.getTime() <= Date.now()) {
      return c.json<ErrorResponse>(
        { error: { code: 400, message: 'expiresAt must be in the future', details: null } },
        400
      );
    }
  }

  // REQ-SHORT-001: Generate code and store
  let shortCode: string;
  try {
    shortCode = generateCode();
  } catch {
    return c.json<ErrorResponse>(
      { error: { code: 500, message: 'Failed to generate short code', details: null } },
      500
    );
  }

  const now = new Date().toISOString();

  const record: UrlRecord = {
    id: randomUUID(),
    originalUrl: body.url,
    shortCode,
    createdAt: now,
    expiresAt: body.expiresAt ?? null,
    isActive: true,
  };

  save(record);

  const response: ShortenResponse = {
    shortUrl: `${BASE_URL}/${shortCode}`,
    originalUrl: record.originalUrl,
    shortCode: record.shortCode,
    createdAt: record.createdAt,
    expiresAt: record.expiresAt,
  };

  return c.json(response, 201);
});

export default app;
