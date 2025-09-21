import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { accountNotesApi } from '@/services/api/accountNotesApi';
import { useToast } from '@/hooks/useToast';
import { createQueryKeys } from '@/lib/query-client';
import { AccountNoteCreateRequest, AccountNoteUpdateRequest } from '@/types/accountNotes';

// Base query keys using the utility
const baseKeys = createQueryKeys('account-notes');

// Extended query keys for account notes feature
export const accountNotesKeys = {
  ...baseKeys,
  list: (accountId: string) => [...baseKeys.all, 'notes', accountId] as const,
  detail: (accountId: string, noteId: string) => [...baseKeys.all, 'note', accountId, noteId] as const,
};

/**
 * Hook for managing account notes
 * Only fetches when explicitly called with an account ID
 */
export function useAccountNotes(accountId: string) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Fetch notes for an account
  const {
    data: notesData,
    isLoading: isNotesLoading,
    error: notesError,
  } = useQuery({
    queryKey: accountNotesKeys.list(accountId),
    queryFn: async () => {
      if (!accountId) throw new Error('Account ID is required');
      return accountNotesApi.listNotes(accountId);
    },
    enabled: !!accountId,
    staleTime: 1000 * 60 * 3, // 3 minutes
  });

  // Create note mutation
  const createNoteMutation = useMutation({
    mutationFn: async (data: AccountNoteCreateRequest) => {
      if (!accountId) throw new Error('Account ID is required');
      const response = await accountNotesApi.createNote(accountId, data);
      return { message: 'Note created successfully' };
    },
    onSuccess: (data: { message: string }) => {
      queryClient.invalidateQueries({ queryKey: accountNotesKeys.list(accountId) });
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create note');
    },
  });

  // Update note mutation - simplified
  const updateNoteMutation = useMutation({
    mutationFn: async (params: { noteId: string; data: AccountNoteUpdateRequest }) => {
      const response = await accountNotesApi.updateNote(accountId, params.noteId, params.data);
      return { message: 'Note updated successfully' };
    },
    onSuccess: (data: { message: string }) => {
      queryClient.invalidateQueries({ queryKey: accountNotesKeys.list(accountId) });
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update note');
    },
  });

  // Delete note mutation
  const deleteNoteMutation = useMutation({
    mutationFn: async (noteId: string) => {
      if (!accountId || !noteId) throw new Error('Account ID and Note ID are required');
      const response = await accountNotesApi.deleteNote(accountId, noteId);
      return { message: 'Note deleted successfully' };
    },
    onSuccess: (data: { message: string }) => {
      queryClient.invalidateQueries({ queryKey: accountNotesKeys.list(accountId) });
      toast.success(data.message);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to delete note');
    },
  });

  return {
    // Query data and states
    notesData,
    isNotesLoading,
    notesError,

    // Note mutation actions
    createNote: createNoteMutation.mutateAsync,
    updateNote: updateNoteMutation.mutateAsync,
    deleteNote: deleteNoteMutation.mutateAsync,

    // Note mutation states
    isCreatingNote: createNoteMutation.isPending,
    isUpdatingNote: updateNoteMutation.isPending,
    isDeletingNote: deleteNoteMutation.isPending,

    // Error states
    createNoteError: createNoteMutation.error,
    updateNoteError: updateNoteMutation.error,
    deleteNoteError: deleteNoteMutation.error,

    // Success states
    createNoteSuccess: createNoteMutation.isSuccess,
    updateNoteSuccess: updateNoteMutation.isSuccess,
    deleteNoteSuccess: deleteNoteMutation.isSuccess,
  };
}