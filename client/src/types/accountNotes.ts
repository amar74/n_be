import { z } from 'zod';
import { schemas } from './generated/account_notes';

// Re-export base generated types
export type AccountNoteCreateRequest = z.infer<typeof schemas.AccountNoteCreateRequest>;
export type AccountNoteDeleteResponse = z.infer<typeof schemas.AccountNoteDeleteResponse>;
export type AccountNoteListResponse = z.infer<typeof schemas.AccountNoteListResponse>;
export type AccountNoteResponse = z.infer<typeof schemas.AccountNoteResponse>;
export type AccountNoteUpdateRequest = z.infer<typeof schemas.AccountNoteUpdateRequest>;
