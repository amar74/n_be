import { Edit, Trash2, FileText, Calendar } from 'lucide-react';
import { AccountNoteResponse } from '@/types/accountNotes';

interface NotesListProps {
  notes: AccountNoteResponse[];
  onEdit: (note: AccountNoteResponse) => void;
  onDelete: (noteId: string) => void;
  isLoading?: boolean;
}

export function NotesList({ notes, onEdit, onDelete, isLoading = false }: NotesListProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleDelete = (noteId: string, noteTitle: string) => {
    if (window.confirm(`Are you sure you want to delete "${noteTitle}"? This action cannot be undone.`)) {
      onDelete(noteId);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ed8a09]"></div>
        </div>
      </div>
    );
  }

  if (notes.length === 0) {
    return (
      <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <FileText className="h-12 w-12 text-[#a7a7a7] mb-4" />
          <h3 className="font-inter font-semibold text-[#0f0901] text-[18px] mb-2">No Notes Yet</h3>
          <p className="font-inter font-medium text-[#a7a7a7] text-[16px]">
            Create your first note for this account using the form above.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
      <div className="flex flex-col gap-6 w-full">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="font-inter font-bold text-[#0f0901] text-[20px] leading-normal flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Account Notes ({notes.length})
          </h3>
        </div>

        {/* Divider */}
        <div className="h-px w-full bg-[#e6e6e6]" />

        {/* Notes List */}
        <div className="flex flex-col gap-4 w-full">
          {notes.map((note) => (
            <div
              key={note.id}
              className="bg-white border border-[#e6e6e6] rounded-[16px] p-6 hover:border-[#d0d0d0] transition-colors"
            >
              <div className="flex flex-col gap-4">
                {/* Header Row */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-inter font-semibold text-[#0f0901] text-[18px] leading-normal mb-2">
                      {note.title}
                    </h4>
                    
                    {/* Meta Information */}
                    <div className="flex items-center gap-4 text-[14px] text-[#6c6c6c]">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span className="font-inter font-medium">
                          {formatDate(note.date)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => onEdit(note)}
                      className="bg-[#f3f3f3] hover:bg-[#e8e8e8] border border-[#e6e6e6] rounded-[8px] p-2 transition-colors"
                      title="Edit Note"
                    >
                      <Edit className="h-4 w-4 text-[#0f0901]" />
                    </button>
                    <button
                      onClick={() => handleDelete(note.id, note.title)}
                      className="bg-[#fee2e2] hover:bg-[#fecaca] border border-[#fca5a5] rounded-[8px] p-2 transition-colors"
                      title="Delete Note"
                    >
                      <Trash2 className="h-4 w-4 text-[#dc2626]" />
                    </button>
                  </div>
                </div>

                {/* Content */}
                <div className="text-[#0f0901] font-inter font-normal text-[16px] leading-relaxed">
                  {note.content}
                </div>

                {/* Footer with timestamps */}
                <div className="flex items-center justify-between pt-2 border-t border-[#f0f0f0]">
                  <div className="text-[12px] text-[#a7a7a7] font-inter">
                    Created: {formatDate(note.created_at)}
                  </div>
                  {note.updated_at && note.updated_at !== note.created_at && (
                    <div className="text-[12px] text-[#a7a7a7] font-inter">
                      Updated: {formatDate(note.updated_at)}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
