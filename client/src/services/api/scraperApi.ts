import apiClient from './client';
import type { ScrapeRequest, ScrapeResponse } from '../../types/scraper';

/**
 * Represents a structured API error response.
 */
export class ApiError extends Error {
  status: number;
  detail: any;

  constructor(message: string, status: number, detail: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export const scraperApi = {
  /**
   * Scrape a list of URLs and return structured results.
   * @throws {ApiError} If the API responds with a validation or server error.
   */
  async scraper(urls: string[]): Promise<ScrapeResponse> {
    const requestData: ScrapeRequest = { urls };

    try {
      const { data } = await apiClient.post<ScrapeResponse>('/scraper/scrape', requestData);
      return data;
    } catch (error: any) {
      // Axios-style error structure
      if (error.response) {
        const { status, data } = error.response;

        throw new ApiError('Scraper API request failed', status, data?.detail || data);
      }

      // Network or unknown error
      throw new Error('An unexpected error occurred while calling the scraper API.');
    }
  },
};
