import { useState, useMemo } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Note, NoteFormData } from './NotesTab.types';
import { MOCK_NOTES, DEFAULT_FORM_VALUES } from './NotesTab.constants';

export function useAccountNotes(accountId: string) {
  const { toast } = useToast();
  
  // State
  const [notes, setNotes] = useState<Note[]>(MOCK_NOTES);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);

  // Computed values
  const sortedNotes = useMemo(() => {
    return [...notes].sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  }, [notes]);

  // Actions
  const createNote = async (noteData: NoteFormData) => {
    setIsCreating(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newNote: Note = {
        id: Date.now().toString(),
        ...noteData,
        author: 'Current User', // In real app, get from auth context
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      setNotes(prev => [newNote, ...prev]);
      
      toast({
        title: '✅ Note Created',
        description: 'Your note has been successfully created.',
      });
      
      return newNote;
    } catch (error) {
      console.error('Error creating note:', error);
      toast({
        title: 'Error',
        description: 'Failed to create note. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsCreating(false);
    }
  };

  const updateNote = async (noteId: string, noteData: NoteFormData) => {
    setIsUpdating(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setNotes(prev => prev.map(note => 
        note.id === noteId 
          ? { ...note, ...noteData, updatedAt: new Date().toISOString() }
          : note
      ));
      
      toast({
        title: '✅ Note Updated',
        description: 'Your note has been successfully updated.',
      });
    } catch (error) {
      console.error('Error updating note:', error);
      toast({
        title: 'Error',
        description: 'Failed to update note. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsUpdating(false);
    }
  };

  const deleteNote = async (noteId: string) => {
    setIsDeleting(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setNotes(prev => prev.filter(note => note.id !== noteId));
      
      toast({
        title: '✅ Note Deleted',
        description: 'Note has been successfully deleted.',
      });
    } catch (error) {
      console.error('Error deleting note:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete note. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsDeleting(false);
    }
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
    
    // Default values for forms
    defaultFormValues: DEFAULT_FORM_VALUES,
  };
}
