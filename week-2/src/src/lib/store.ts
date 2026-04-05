// REQ-SHORT-001, REQ-SHORT-003, REQ-SHORT-004, REQ-SHORT-005, REQ-SHORT-006

import type { UrlRecord, AnalyticsEvent } from '../types.js';

const urls = new Map<string, UrlRecord>();
const urlsByOriginal = new Map<string, UrlRecord>();
const analytics = new Map<string, AnalyticsEvent[]>();

/** Save a new URL record @req REQ-SHORT-001 */
export function save(record: UrlRecord): UrlRecord {
  urls.set(record.shortCode, record);
  urlsByOriginal.set(record.originalUrl, record);
  return record;
}

/** Find a URL record by short code @req REQ-SHORT-002 */
export function findByCode(code: string): UrlRecord | undefined {
  return urls.get(code);
}

/** Find a URL record by original URL (duplicate check) @req REQ-SHORT-005 */
export function findByOriginal(url: string): UrlRecord | undefined {
  return urlsByOriginal.get(url);
}

/** Record an analytics event @req REQ-SHORT-003 */
export function recordAnalytics(event: AnalyticsEvent): void {
  const events = analytics.get(event.urlId) || [];
  events.push(event);
  analytics.set(event.urlId, events);
}

/** Get all analytics events for a URL record ID @req REQ-SHORT-003 */
export function getAnalytics(urlId: string): AnalyticsEvent[] {
  return analytics.get(urlId) || [];
}

/** Soft-delete a URL by short code @req REQ-SHORT-006 */
export function deleteByCode(code: string): boolean {
  const record = urls.get(code);
  if (!record) return false;
  record.isActive = false;
  return true;
}
