// REQ-SHORT-001, REQ-SHORT-002, REQ-SHORT-003, REQ-SHORT-006, REQ-SHORT-007, NFR-005

import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import type { ErrorResponse } from './types.js';
import shortenRoutes from './routes/shorten.js';
import analyticsRoutes from './routes/analytics.js';
import redirectRoutes from './routes/redirect.js';
import deleteRoutes from './routes/delete.js';

const app = new Hono();

// Register routes — order matters: specific paths before wildcard /:code
app.route('/', shortenRoutes);
app.route('/', analyticsRoutes);
app.route('/', deleteRoutes);
app.route('/', redirectRoutes);

/**
 * Global error handler @req REQ-SHORT-007 @req NFR-005
 * Returns consistent error envelope, no stack traces in production
 */
app.onError((err, c) => {
  console.error(`[ERROR] ${err.message}`);
  return c.json<ErrorResponse>(
    {
      error: {
        code: 500,
        message: 'Internal server error',
        details: null,
      },
    },
    500
  );
});

/** 404 handler @req REQ-SHORT-007 */
app.notFound((c) => {
  return c.json<ErrorResponse>(
    { error: { code: 404, message: 'Not found', details: null } },
    404
  );
});

// Only start server when run directly, not when imported by tests
if (process.env.NODE_ENV !== 'test') {
  const port = parseInt(process.env.PORT || '3000', 10);
  serve({ fetch: app.fetch, port }, () => {
    console.log(`URL Shortener running on http://localhost:${port}`);
  });
}

export default app;
