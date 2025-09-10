import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { ValidationError } from "./common";

const ScrapedAddress = z
  .object({
    line1: z.union([z.string(), z.null()]),
    line2: z.union([z.string(), z.null()]),
    city: z.union([z.string(), z.null()]),
    state: z.union([z.string(), z.null()]),
    country_code: z.union([z.string(), z.null()]),
    pincode: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const ScrapedInfo = z
  .object({
    name: z.union([z.string(), z.null()]),
    email: z.array(z.string()),
    phone: z.array(z.string()),
    address: z.union([ScrapedAddress, z.null()]),
  })
  .partial()
  .passthrough();
const ScrapeResult = z
  .object({
    url: z.string(),
    info: z.union([ScrapedInfo, z.null()]).optional(),
    error: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const ScrapeResponse = z
  .object({
    results: z.array(ScrapeResult),
    total_urls: z.number().int(),
    successful_scrapes: z.number().int(),
    failed_scrapes: z.number().int(),
  })
  .passthrough();
const ScrapeRequest = z
  .object({ urls: z.array(z.string().min(1).max(2083).url()) })
  .passthrough();

export const schemas = {
  ScrapedAddress,
  ScrapedInfo,
  ScrapeResult,
  ScrapeResponse,
  ScrapeRequest,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/scraper/scrape",
    alias: "scrapeUrls",
    description: `Scrape multiple URLs and extract contact information.

Only authenticated users can access this endpoint.

Args:
    payload: ScrapeRequest containing URLs to scrape
    request: FastAPI request object for JWT token extraction

Returns:
    ScrapeResponse: Scraped contact information and statistics`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ScrapeRequest,
      },
    ],
    response: ScrapeResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const ScraperApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
