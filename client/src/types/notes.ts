import { z } from 'zod';
import { schemas } from './generated/notes';

// Re-export generated types
export type Note = z.infer<typeof schemas.NoteResponse>;
export type NoteListResponse = z.infer<typeof schemas.NoteListResponse>;
export type NoteCreateRequest = z.infer<typeof schemas.NoteCreateRequest>;
export type NoteCreateResponse = z.infer<typeof schemas.NoteCreateResponse>;
export type NoteUpdateRequest = z.infer<typeof schemas.NoteUpdateRequest>;
export type NoteUpdateResponse = z.infer<typeof schemas.NoteUpdateResponse>;
export type NoteDeleteResponse = z.infer<typeof schemas.NoteDeleteResponse>;

// Custom validation schemas for forms
export const NoteCreateFormSchema = z.object({
  meeting_title: z
    .string()
    .min(1, 'Meeting title is required')
    .max(255, 'Meeting title must be less than 255 characters'),
  meeting_datetime: z
    .string()
    .min(1, 'Meeting date and time is required')
    .refine(
      (value) => {
        const date = new Date(value);
        return !isNaN(date.getTime());
      },
      'Please enter a valid date and time'
    ),
  meeting_notes: z
    .string()
    .min(1, 'Meeting notes are required')
    .max(10000, 'Meeting notes must be less than 10000 characters'),
});

export const NoteUpdateFormSchema = z.object({
  meeting_title: z
    .string()
    .min(1, 'Meeting title is required')
    .max(255, 'Meeting title must be less than 255 characters')
    .optional(),
  meeting_datetime: z
    .string()
    .min(1, 'Meeting date and time is required')
    .refine(
      (value) => {
        if (!value) return true; // Optional field
        const date = new Date(value);
        return !isNaN(date.getTime());
      },
      'Please enter a valid date and time'
    )
    .optional(),
  meeting_notes: z
    .string()
    .min(1, 'Meeting notes are required')
    .max(10000, 'Meeting notes must be less than 10000 characters')
    .optional(),
});

// Form data types
export type NoteCreateFormData = z.infer<typeof NoteCreateFormSchema>;
export type NoteUpdateFormData = z.infer<typeof NoteUpdateFormSchema>;

// UI state types
export interface NotesState {
  notes: Note[];
  currentNote: Note | null;
  isLoading: boolean;
  error: string | null;
}

export interface NotesListState extends NotesState {
  totalCount: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Pagination parameters
export interface NotesListParams {
  page?: number;
  limit?: number;
}

// Export schemas for validation
export { schemas as NotesSchemas };
