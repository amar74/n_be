import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { NotesForm } from '../NotesForm';
import { Note, NoteFormData } from '../../NotesTab.types';

interface EditNoteModalProps {
  isOpen: boolean;
  note: Note | null;
  onClose: () => void;
  onSave: (noteId: string, data: NoteFormData) => Promise<any>;
  isLoading?: boolean;
}

export function EditNoteModal({ 
  isOpen, 
  note, 
  onClose, 
  onSave, 
  isLoading = false 
}: EditNoteModalProps) {
  const handleSubmit = async (formData: NoteFormData) => {
    if (!note) return;
    
    await onSave(note.id, formData);
    onClose();
  };

  if (!note) return null;

  const initialData = {
    title: note.title,
    content: note.content,
    category: note.category,
    date: note.date,
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="font-inter font-bold text-[#0f0901] text-[20px]">
            Edit Note
          </DialogTitle>
          <DialogDescription className="font-inter font-medium text-[#a7a7a7] text-[16px]">
            Update your note details below.
          </DialogDescription>
        </DialogHeader>
        
        <div className="mt-4">
          <NotesForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            initialData={initialData}
            onCancel={onClose}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
