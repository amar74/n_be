import { apiClient } from './client';
import {
  AccountNoteCreateRequest,
  AccountNoteDeleteResponse,
  AccountNoteListResponse,
  AccountNoteResponse,
  AccountNoteUpdateRequest,
} from '@/types/accountNotes';

class AccountNotesApiService {
  private baseURL = '/accounts';

  // List notes for an account
  async listNotes(accountId: string): Promise<AccountNoteListResponse> {
    const response = await apiClient.get(`${this.baseURL}/${accountId}/notes/`);
    return response.data;
  }

  // Get single note by ID
  async getNote(accountId: string, noteId: string): Promise<AccountNoteResponse> {
    const response = await apiClient.get(`${this.baseURL}/${accountId}/notes/${noteId}`);
    return response.data;
  }

  // Create new note
  async createNote(accountId: string, data: AccountNoteCreateRequest): Promise<AccountNoteResponse> {
    try {
      const response = await apiClient.post(`${this.baseURL}/${accountId}/notes/`, data);
      return response.data;
    } catch (error: any) {
      throw error;
    }
  }

  // Update existing note - simplified
  async updateNote(accountId: string, noteId: string, data: AccountNoteUpdateRequest): Promise<AccountNoteResponse> {
    const response = await apiClient.put(`${this.baseURL}/${accountId}/notes/${noteId}`, data);
    return response.data;
  }

  // Delete note
  async deleteNote(accountId: string, noteId: string): Promise<AccountNoteDeleteResponse> {
    const response = await apiClient.delete(`${this.baseURL}/${accountId}/notes/${noteId}`);
    return response.data;
  }
}

export const accountNotesApi = new AccountNotesApiService();