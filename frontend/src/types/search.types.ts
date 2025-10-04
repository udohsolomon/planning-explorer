/**
 * Search API Type Definitions
 * Planning Explorer - Backend integration types
 */

import type { AnimationError } from './animation.types';

/**
 * Search request payload
 */
export interface SearchRequest {
  query: string;
  searchType: 'semantic' | 'keyword' | 'hybrid';
  filters?: {
    localAuthority?: string[];
    status?: string[];
    dateFrom?: string;
    dateTo?: string;
    applicationType?: string[];
  };
  page?: number;
  limit?: number;
}

/**
 * Search result item
 */
export interface SearchResult {
  id: string;
  applicationNumber: string;
  address: string;
  description: string;
  localAuthority: string;
  status: string;
  decisionDate?: string;
  submissionDate: string;
  applicationType: string;

  // AI-enhanced fields
  opportunityScore?: number;
  aiSummary?: string;
  relevanceScore?: number;

  // Coordinates for map
  latitude?: number;
  longitude?: number;
}

/**
 * Real-time progress update from backend
 */
export interface SearchProgressUpdate {
  stage: number; // 1-5
  progress: number; // 0-100
  status: 'processing' | 'complete' | 'error';
  substep?: number; // For smoother progress calculation
  message?: string; // Optional status message

  // Results (only on completion)
  results?: SearchResult[];

  // Error (only on error)
  error?: {
    type: string;
    message: string;
    code?: number;
  };

  // Metadata
  metadata?: {
    totalResults: number;
    processingTime: number;
    relevanceScores?: number[];
    wasAccelerated?: boolean;
  };
}

/**
 * Search API response (HTTP)
 */
export interface SearchResponse {
  results: SearchResult[];
  totalResults: number;
  page: number;
  totalPages: number;
  processingTime: number;
  query: string;
  searchType: string;
}

/**
 * Search API error response
 */
export interface SearchErrorResponse {
  error: {
    type: string;
    message: string;
    code: number;
    details?: Record<string, any>;
  };
}

/**
 * WebSocket message types
 */
export type WSMessageType =
  | 'progress'
  | 'complete'
  | 'error'
  | 'cancelled';

export interface WSMessage {
  type: WSMessageType;
  data: SearchProgressUpdate;
  timestamp: number;
  requestId: string;
}

/**
 * API configuration
 */
export interface APIConfig {
  baseURL: string;
  wsURL: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}
