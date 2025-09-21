import { useState, useMemo, useEffect } from 'react';
import { useAccountNotes } from '@/hooks/useAccountNotes';
import { NoteFormData } from './NotesTab.types';
import { AccountNoteResponse } from '@/types/accountNotes';
import { AxiosError } from 'axios';
import { parseBackendErrors } from '@/utils/errorParser';
import { HTTPValidationError } from '@/types/validationError';

export function useNotesTab(accountId: string) {
  const [editingNote, setEditingNote] = useState<AccountNoteResponse | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [createErrors, setCreateErrors] = useState<Record<string, string>>({});
  const [updateErrors, setUpdateErrors] = useState<Record<string, string>>({});

  const {
    notesData,
    isNotesLoading,
    isCreatingNote,
    isUpdatingNote,
    isDeletingNote,
    createNoteError,
    createNoteSuccess,
    updateNoteError,
    updateNoteSuccess,
    createNote: createNoteCore,
    updateNote: updateNoteCore,
    deleteNote: deleteNoteCore,
  } = useAccountNotes(accountId);

  // Get notes from the response
  const accountNotes = notesData?.notes || [];

  // Convert and sort notes
  const sortedNotes = useMemo(() => {
    return [...accountNotes]
      .sort((a, b) => 
        new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime()
      );
  }, [accountNotes]);

  // Modal actions
  const startEditNote = (note: AccountNoteResponse) => {
    setEditingNote(note);
    setShowEditModal(true);
  };

  const closeEditModal = () => {
    setEditingNote(null);
    setShowEditModal(false);
  };

  // CRUD operations
  const createNote = (formData: NoteFormData) => 
    createNoteCore({
      title: formData.title,
      date: new Date(formData.date).toISOString(),
      content: formData.content,
    });

  const updateNote = (noteId: string, formData: NoteFormData) =>
    updateNoteCore({
      noteId,
      data: {
        title: formData.title,
        date: new Date(formData.date).toISOString(),
        content: formData.content,
      }
    });

  const saveEdit = async (noteId: string, data: NoteFormData) => {
    await updateNote(noteId, data);
    closeEditModal();
  };

  // Handle create errors
  useEffect(() => {
    if (createNoteError && (createNoteError as AxiosError)?.response?.data) {
      const errors = parseBackendErrors(
        (createNoteError as AxiosError).response?.data as HTTPValidationError,
        ['title', 'content', 'date']
      );
      setCreateErrors(errors);
    } else {
      setCreateErrors({});
    }
  }, [createNoteError]);

  // Handle update errors
  useEffect(() => {
    if (updateNoteError && (updateNoteError as AxiosError)?.response?.data) {
      const errors = parseBackendErrors(
        (updateNoteError as AxiosError).response?.data as HTTPValidationError,
        ['title', 'content', 'date']
      );
      setUpdateErrors(errors);
    } else {
      setUpdateErrors({});
    }
  }, [updateNoteError]);

  // Clear errors on success
  useEffect(() => {
    if (createNoteSuccess) {
      setCreateErrors({});
    }
  }, [createNoteSuccess]);

  useEffect(() => {
    if (updateNoteSuccess) {
      setUpdateErrors({});
      closeEditModal();
    }
  }, [updateNoteSuccess]);

  return {
    // Data
    notes: sortedNotes,
    editingNote,
    showEditModal,
    
    // State
    isLoading: isNotesLoading,
    isCreating: isCreatingNote,
    isUpdating: isUpdatingNote,
    isDeleting: isDeletingNote,
    
    // Error states
    createErrors,
    updateErrors,
    
    // Actions
    createNote,
    updateNote,
    deleteNote: deleteNoteCore,
    startEditNote,
    cancelEdit: closeEditModal,
    saveEdit,
  };
}