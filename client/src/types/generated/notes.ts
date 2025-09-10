import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

import { HTTPValidationError } from "./common";
import { ValidationError } from "./common";

const NoteResponse = z
  .object({
    id: z.string().uuid(),
    meeting_title: z.string(),
    meeting_datetime: z.string().datetime({ offset: true }),
    meeting_notes: z.string(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.union([z.string(), z.null()]),
    org_id: z.string().uuid(),
    created_by: z.string().uuid(),
  })
  .passthrough();
const NoteListResponse = z
  .object({
    notes: z.array(NoteResponse),
    total_count: z.number().int(),
    page: z.number().int(),
    limit: z.number().int(),
    total_pages: z.number().int(),
    has_next: z.boolean(),
    has_prev: z.boolean(),
  })
  .passthrough();
const NoteCreateResponse = z
  .object({
    id: z.string().uuid(),
    meeting_title: z.string(),
    meeting_datetime: z.string().datetime({ offset: true }),
    meeting_notes: z.string(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.union([z.string(), z.null()]),
    org_id: z.string().uuid(),
    created_by: z.string().uuid(),
  })
  .passthrough();
const NoteCreateRequest = z
  .object({
    meeting_title: z.string(),
    meeting_datetime: z.string().datetime({ offset: true }),
    meeting_notes: z.string(),
  })
  .passthrough();
const NoteUpdateResponse = z
  .object({
    id: z.string().uuid(),
    meeting_title: z.string(),
    meeting_datetime: z.string().datetime({ offset: true }),
    meeting_notes: z.string(),
    created_at: z.string().datetime({ offset: true }),
    updated_at: z.union([z.string(), z.null()]),
    org_id: z.string().uuid(),
    created_by: z.string().uuid(),
  })
  .passthrough();
const NoteUpdateRequest = z
  .object({
    meeting_title: z.union([z.string(), z.null()]),
    meeting_datetime: z.union([z.string(), z.null()]),
    meeting_notes: z.union([z.string(), z.null()]),
  })
  .partial()
  .passthrough();
const NoteDeleteResponse = z
  .object({ id: z.string().uuid(), message: z.string() })
  .passthrough();

export const schemas = {
  NoteResponse,
  NoteListResponse,
  NoteCreateResponse,
  NoteCreateRequest,
  NoteUpdateResponse,
  NoteUpdateRequest,
  NoteDeleteResponse,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/notes/",
    alias: "createNote",
    description: `Create a new meeting note for the user&#x27;s organization.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: NoteCreateRequest,
      },
    ],
    response: NoteCreateResponse,
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
    path: "/notes/",
    alias: "getNotes",
    description: `Get all meeting notes for the user&#x27;s organization with pagination.`,
    requestFormat: "json",
    parameters: [
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
    response: NoteListResponse,
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
    path: "/notes/:note_id",
    alias: "getNoteById",
    description: `Get a specific meeting note by ID within the user&#x27;s organization.`,
    requestFormat: "json",
    parameters: [
      {
        name: "note_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: NoteResponse,
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
    path: "/notes/:note_id",
    alias: "updateNote",
    description: `Update a meeting note within the user&#x27;s organization.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: NoteUpdateRequest,
      },
      {
        name: "note_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: NoteUpdateResponse,
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
    path: "/notes/:note_id",
    alias: "deleteNote",
    description: `Delete a meeting note within the user&#x27;s organization.`,
    requestFormat: "json",
    parameters: [
      {
        name: "note_id",
        type: "Path",
        schema: z.string().uuid(),
      },
    ],
    response: NoteDeleteResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const NotesApi = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
