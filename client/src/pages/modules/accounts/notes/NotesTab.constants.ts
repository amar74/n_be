import { NoteCategory, Note } from './NotesTab.types';

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
] as const;

export const MOCK_NOTES: Note[] = [
  {
    id: '1',
    title: 'Initial client meeting recap',
    content: 'Discussed project requirements and timeline. Client showed great interest in our AI-powered solutions. Key decision makers: Sarah Johnson (CTO) and Michael Chen (Project Manager). Next steps: Prepare detailed proposal by Friday.',
    category: 'meeting',
    date: '2024-01-15',
    author: 'David Rodriguez',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-15T10:30:00Z',
  },
  {
    id: '2',
    title: 'Technical requirements clarification',
    content: 'Client needs integration with their existing ERP system. They use SAP and require real-time data sync. Also discussed security requirements - they need SOC 2 compliance.',
    category: 'technical',
    date: '2024-01-18',
    author: 'Emily Chen',
    createdAt: '2024-01-18T14:15:00Z',
    updatedAt: '2024-01-18T14:15:00Z',
  },
  {
    id: '3',
    title: 'Proposal feedback received',
    content: 'Client reviewed our proposal and has some concerns about the timeline. They want to accelerate the implementation by 2 weeks. Budget approved for Phase 1.',
    category: 'proposal',
    date: '2024-01-22',
    author: 'David Rodriguez',
    createdAt: '2024-01-22T09:45:00Z',
    updatedAt: '2024-01-22T09:45:00Z',
  },
  {
    id: '4',
    title: 'Contract negotiation update',
    content: 'Legal teams from both sides are reviewing the terms. Main discussion points: payment terms, intellectual property rights, and service level agreements. Expected to finalize by end of week.',
    category: 'contract',
    date: '2024-01-25',
    author: 'Sarah Wilson',
    createdAt: '2024-01-25T16:20:00Z',
    updatedAt: '2024-01-25T16:20:00Z',
  },
] as const;

export const DEFAULT_FORM_VALUES = {
  title: '',
  content: '',
  category: 'general',
  date: new Date().toISOString().split('T')[0], // Today's date in YYYY-MM-DD format
} as const;
