// REQ-SHORT-006, REQ-SHORT-007

import { Hono } from 'hono';
import { findByCode, deleteByCode } from '../lib/store.js';
import type { ErrorResponse } from '../types.js';

const app = new Hono();

/**
 * DELETE /:code — Delete a short URL
 * @req REQ-SHORT-006
 * @req REQ-SHORT-007
 */
app.delete('/:code', (c) => {
  const code = c.req.param('code');
  const record = findByCode(code);

  // REQ-SHORT-006: 404 if not found
  if (!record) {
    return c.json<ErrorResponse>(
      { error: { code: 404, message: 'Short code not found', details: null } },
      404
    );
  }

  // REQ-SHORT-006: Soft delete
  deleteByCode(code);

  // REQ-SHORT-006: 204 No Content
  return c.body(null, 204);
});

export default app;
