// REQ-SHORT-001, REQ-SHORT-002, REQ-SHORT-003, REQ-SHORT-004, REQ-SHORT-005, REQ-SHORT-006, REQ-SHORT-007

/** Stored URL record @req REQ-SHORT-001 */
export interface UrlRecord {
  id: string;
  originalUrl: string;
  shortCode: string;
  createdAt: string;
  expiresAt: string | null;
  isActive: boolean;
}

/** Analytics event recorded per redirect @req REQ-SHORT-003 */
export interface AnalyticsEvent {
  id: string;
  urlId: string;
  accessedAt: string;
  referrer: string;
  ipHash: string;
}

/** POST /shorten request body @req REQ-SHORT-001 */
export interface ShortenRequest {
  url: string;
  expiresAt?: string;
}

/** POST /shorten 201 response @req REQ-SHORT-001 */
export interface ShortenResponse {
  shortUrl: string;
  originalUrl: string;
  shortCode: string;
  createdAt: string;
  expiresAt: string | null;
}

/** GET /analytics/:code response @req REQ-SHORT-003 */
export interface AnalyticsResponse {
  shortCode: string;
  originalUrl: string;
  clickCount: number;
  lastAccessedAt: string | null;
  referrers: string[];
}

/** Standard error envelope @req REQ-SHORT-007 */
export interface ErrorResponse {
  error: {
    code: number;
    message: string;
    details: string | null;
  };
}
