import { NoteCategory } from './NotesTab.types';

export const NOTE_CATEGORIES: NoteCategory[] = [
  { value: 'general', label: 'General' },
  { value: 'meeting', label: 'Meeting Notes' },
  { value: 'proposal', label: 'Proposal' },
  { value: 'contract', label: 'Contract' },
  { value: 'follow-up', label: 'Follow-up' },
  { value: 'communication', label: 'Communication' },
  { value: 'technical', label: 'Technical' },
  { value: 'billing', label: 'Billing' },
  { value: 'support', label: 'Support' },
  { value: 'feedback', label: 'Feedback' },
];

export const DEFAULT_FORM_VALUES = {
  title: '',
  content: '',
  category: 'general',
  date: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
} as const;
