import React from 'react';
import { NotesForm } from './components/NotesForm';
import { NotesList } from './components/NotesList';
import { EditNoteModal } from './components/EditNoteModal';
import { useAccountNotes } from './useAccountNotes';
import { NotesTabProps } from './NotesTab.types';

export function NotesTab({ accountId }: NotesTabProps) {
  const {
    // Data
    notes,
    editingNote,
    showEditModal,
    
    // State
    isLoading,
    isCreating,
    isUpdating,
    isDeleting,
    
    // Actions
    createNote,
    startEditNote,
    cancelEdit,
    saveEdit,
    deleteNote,
  } = useAccountNotes(accountId);

  return (
    <div className="flex flex-col gap-8 w-full">
      {/* Notes Form */}
      <NotesForm
        onSubmit={createNote}
        isLoading={isCreating}
      />

      {/* Notes List */}
      <NotesList
        notes={notes}
        onEdit={startEditNote}
        onDelete={deleteNote}
        isLoading={isLoading}
      />

      {/* Edit Modal */}
      <EditNoteModal
        isOpen={showEditModal}
        note={editingNote}
        onClose={cancelEdit}
        onSave={saveEdit}
        isLoading={isUpdating}
      />
    </div>
  );
}
