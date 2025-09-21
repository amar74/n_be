import { useState, useMemo } from 'react';
import { useNotes } from '@/hooks/useNotes';
import { Note as APINote, NoteCreateRequest, NoteUpdateRequest } from '@/types/notes';
import { Note, NoteFormData } from './NotesTab.types';
import { DEFAULT_FORM_VALUES } from './NotesTab.constants';
import { useAuth } from '@/hooks/useAuth'; // Add this import

// Convert API note to UI note
function apiToUiNote(apiNote: APINote): Note {
  return {
    id: apiNote.id,
    title: apiNote.meeting_title,
    content: apiNote.meeting_notes,
    category: 'general', // TODO: Map from API category when available
    date: apiNote.meeting_datetime,
    author: apiNote.created_by,
    createdAt: apiNote.created_at,
    updatedAt: apiNote.updated_at || apiNote.created_at, // Fallback to created_at if no update
  };
}

// Convert form data to API create request
function formToApiCreate(formData: NoteFormData): NoteCreateRequest {
  return {
    meeting_title: formData.title,
    meeting_datetime: formData.date,
    meeting_notes: formData.content,
  };
}

// Convert form data to API update request
function formToApiUpdate(formData: NoteFormData): NoteUpdateRequest {
  return {
    meeting_title: formData.title,
    meeting_datetime: formData.date,
    meeting_notes: formData.content,
  };
}

export function useAccountNotes(accountId: string) {
  // State for edit modal
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);

  // Use the core notes hook with pagination
  const {
    notes: apiNotes,
    isLoading,
    isCreating,
    isUpdating,
    isDeleting,
    createNote: createNoteCore,
    updateNote: updateNoteCore,
    deleteNote: deleteNoteCore,
  } = useNotes(); // Use pagination params only

  // Filter notes by account ID in memory
  const accountNotes = useMemo(() => {
    return apiNotes?.filter(note => note.account_id === accountId) || [];
  }, [apiNotes, accountId]);

  // Convert API notes to UI notes and sort by updated date
  const sortedNotes = useMemo(() => {
    const uiNotes = accountNotes.map(apiToUiNote);
    return uiNotes.sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  }, [accountNotes]);

  // Actions
  const createNote = async (noteData: NoteFormData) => {
    const apiData = formToApiCreate(noteData);
    await createNoteCore(apiData);
    // Note will be available in the list after query invalidation
  };

  const updateNote = async (noteId: string, noteData: NoteFormData) => {
    const apiData = formToApiUpdate(noteData);
    await updateNoteCore({ noteId, data: apiData });
  };

  const deleteNote = async (noteId: string) => {
    await deleteNoteCore(noteId);
  };

  const startEditNote = (note: Note) => {
    setEditingNote(note);
    setShowEditModal(true);
  };

  const cancelEdit = () => {
    setEditingNote(null);
    setShowEditModal(false);
  };

  const saveEdit = async (noteId: string, data: NoteFormData) => {
    await updateNote(noteId, data);
    setEditingNote(null);
    setShowEditModal(false);
  };

  return {
    // Data
    notes: sortedNotes,
    editingNote,
    showEditModal,
    
    // State
    isLoading,
    isCreating,
    isUpdating,
    isDeleting,
    
    // Actions
    createNote,
    updateNote,
    deleteNote,
    startEditNote,
    cancelEdit,
    saveEdit,
    
  };
}
