import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { ValidationError } from "./common";

const AccountNoteResponse = z
  .object({
    id: z.string().uuid(),
    account_id: z.string().uuid(),
    title: z.string(),
    content: z.string(),
    date: z.string().datetime({ offset: true }),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.union([z.string(), z.null()]),
  })
  .passthrough();
const AccountNoteListResponse = z
  .object({
    notes: z.array(AccountNoteResponse),
    total_count: z.number().int(),
    page: z.number().int(),
    limit: z.number().int(),
    total_pages: z.number().int(),
    has_next: z.boolean(),
    has_prev: z.boolean(),
  })
  .passthrough();
const AccountNoteCreateRequest = z
  .object({
    title: z.string(),
    content: z.string(),
    date: z.string().datetime({ offset: true }),
  })
  .passthrough();
const AccountNoteUpdateRequest = z
  .object({
    title: z.union([z.string(), z.null()]),
    content: z.union([z.string(), z.null()]),
    date: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const AccountNoteDeleteResponse = z
  .object({ id: z.string().uuid(), message: z.string() })
  .passthrough();

export const schemas = {
  AccountNoteResponse,
  AccountNoteListResponse,
  AccountNoteCreateRequest,
  AccountNoteUpdateRequest,
  AccountNoteDeleteResponse,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/accounts/:account_id/notes/",
    alias: "createAccountNote",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AccountNoteCreateRequest,
      },
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AccountNoteResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/accounts/:account_id/notes/",
    alias: "listAccountNotes",
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "page",
        type: "Query",
        schema: z.number().int().gte(1).optional().default(1),
      },
      {
        name: "limit",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(10),
      },
    ],
    response: AccountNoteListResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/accounts/:account_id/notes/:note_id",
    alias: "getAccountNote",
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "note_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AccountNoteResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "put",
    path: "/accounts/:account_id/notes/:note_id",
    alias: "updateAccountNote",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AccountNoteUpdateRequest,
      },
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "note_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AccountNoteResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "delete",
    path: "/accounts/:account_id/notes/:note_id",
    alias: "deleteAccountNote",
    requestFormat: "json",
    parameters: [
      {
        name: "account_id",
        type: "Path",
        schema: z.string().uuid(),
      },
      {
        name: "note_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: AccountNoteDeleteResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const Account_notesApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
