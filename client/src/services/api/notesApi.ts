import {
  Note,
  NoteListResponse,
  NoteCreateRequest,
  NoteCreateResponse,
  NoteUpdateRequest,
  NoteUpdateResponse,
  NoteDeleteResponse,
  NotesListParams,
} from '@/types/notes';
import apiClient from './client';

export const notesApi = {
  /**
   * Create a new meeting note
   */
  async createNote(data: NoteCreateRequest): Promise<NoteCreateResponse> {
    const { data: response } = await apiClient.post<NoteCreateResponse>('/notes/', data);
    return response;
  },

  /**
   * Get all meeting notes with pagination
   */
  async getNotes(params: NotesListParams = {}): Promise<NoteListResponse> {
    const { page = 1, limit = 10 } = params;
    const { data } = await apiClient.get<NoteListResponse>('/notes/', {
      params: { page, limit },
    });
    return data;
  },

  /**
   * Get a specific note by ID
   */
  async getNoteById(noteId: string): Promise<Note> {
    const { data } = await apiClient.get<Note>(`/notes/${noteId}`);
    return data;
  },

  /**
   * Update a specific note
   */
  async updateNote(noteId: string, data: NoteUpdateRequest): Promise<NoteUpdateResponse> {
    const { data: response } = await apiClient.put<NoteUpdateResponse>(`/notes/${noteId}`, data);
    return response;
  },

  /**
   * Delete a specific note
   */
  async deleteNote(noteId: string): Promise<NoteDeleteResponse> {
    const { data } = await apiClient.delete<NoteDeleteResponse>(`/notes/${noteId}`);
    return data;
  },
};
