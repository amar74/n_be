import { AccountNoteResponse } from "@/types/accountNotes";

export interface NoteFormData {
  title: string;
  content: string;
  date: string;
}

export interface NotesTabProps {
  accountId: string;
}

export interface NotesFormProps {
  onSubmit: (note: NoteFormData) => void;
  isLoading?: boolean;
  initialData?: Partial<NoteFormData>;
  onCancel?: () => void;
}

export interface NotesListProps {
  notes: AccountNoteResponse[];
  onEdit: (note: AccountNoteResponse) => void;
  onDelete: (noteId: string) => void;
  isLoading?: boolean;
}

export interface EditNoteModalProps {
  isOpen: boolean;
  note: AccountNoteResponse | null;
  onClose: () => void;
  onSave: (noteId: string, data: NoteFormData) => void;
  isLoading?: boolean;
}
