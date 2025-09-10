// src/types/scraper.ts

import { z } from 'zod';
import { schemas } from './generated/scraper'; // Adjust path if needed

// Re-export generated types
export type ScrapedAddress = z.infer<typeof schemas.ScrapedAddress>;
export type ScrapedInfo = z.infer<typeof schemas.ScrapedInfo>;
export type ScrapeResult = z.infer<typeof schemas.ScrapeResult>;
export type ScrapeResponse = z.infer<typeof schemas.ScrapeResponse>;
export type ScrapeRequest = z.infer<typeof schemas.ScrapeRequest>;

// Business logic extensions
export interface ScraperState {
  results: ScrapeResult[];
  total: number;
  successCount: number;
  failureCount: number;
  isLoading: boolean;
  error: string | null;
}

// Request form for user input (may differ from actual ScrapeRequest if you use a form)
export interface ScraperInput {
  urls: string[];
}

// Scraper response wrapper
export interface ScraperResponse extends ScrapeResponse {
  timestamp: string; // for example: when the scraping was done
}

// Context or hook return type (if using something like useScraper)
export interface ScraperContextValue {
  state: ScraperState;
  scrape: (input: ScraperInput) => Promise<void>;
  reset: () => void;
}
