export interface Note {
  id: string;
  title: string;
  content: string;
  category: string;
  date: string;
  author: string;
  createdAt: string;
  updatedAt: string;
}

export interface NoteFormData {
  title: string;
  content: string;
  category: string;
  date: string;
}

export interface NoteCategory {
  value: string;
  label: string;
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
  notes: Note[];
  onEdit: (note: Note) => void;
  onDelete: (noteId: string) => void;
  isLoading?: boolean;
}

export interface EditNoteModalProps {
  isOpen: boolean;
  note: Note | null;
  onClose: () => void;
  onSave: (noteId: string, data: NoteFormData) => void;
  isLoading?: boolean;
}
