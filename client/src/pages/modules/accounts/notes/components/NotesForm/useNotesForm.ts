import { useState, useEffect, useCallback } from 'react';
import { NoteFormData } from '../../NotesTab.types';
import { AccountNoteResponse } from '@/types/accountNotes';

interface UseNotesFormProps {
  initialData?: Partial<AccountNoteResponse>;
  onSubmit: (note: NoteFormData) => Promise<any>;
  onCancel?: () => void;
}

interface FormErrors {
  title?: string;
  content?: string;
  date?: string;
}

const formatDateForInput = (date: string | Date): string => {
  // Handle string date (from backend)
  if (typeof date === 'string') {
    // Create date in local timezone
    const d = new Date(date);
    // Get year, month, day in local timezone
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  // Handle new Date() for empty state
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const getInitialFormState = (initialData?: Partial<AccountNoteResponse>): NoteFormData => {
  if (!initialData) {
    return {
      title: '',
      content: '',
      date: formatDateForInput(new Date()),
    };
  }

  return {
    title: initialData.title || '',
    content: initialData.content || '',
    date: initialData.date ? formatDateForInput(initialData.date) : formatDateForInput(new Date()),
  };
};

export const useNotesForm = ({ initialData, onSubmit, onCancel }: UseNotesFormProps) => {
  const [formData, setFormData] = useState<NoteFormData>(getInitialFormState(initialData));
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset form when initialData changes
  useEffect(() => {
    setFormData(getInitialFormState(initialData));
    setErrors({});
  }, [initialData]);

  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Content is required';
    }

    if (!formData.date) {
      newErrors.date = 'Date is required';
    } else {
      const dateValue = new Date(formData.date);
      if (isNaN(dateValue.getTime())) {
        newErrors.date = 'Invalid date';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleChange = useCallback((field: keyof NoteFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    setErrors(prev => ({ ...prev, [field]: undefined }));
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setIsSubmitting(true);
      await onSubmit(formData);

      // Reset form only if it's a create operation
      if (!initialData) {
        setFormData(getInitialFormState());
      }
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, initialData, onSubmit, validateForm]);

  const handleCancel = useCallback(() => {
    setFormData(getInitialFormState(initialData));
    setErrors({});
    onCancel?.();
  }, [initialData, onCancel]);

  return {
    formData,
    errors,
    isSubmitting,
    isEditMode: Boolean(initialData),
    handleChange,
    handleSubmit,
    handleCancel,
  };
};