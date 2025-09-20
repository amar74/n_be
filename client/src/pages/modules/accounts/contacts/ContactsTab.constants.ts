import { ContactRole, Contact } from './ContactsTab.types';

export const CONTACT_ROLES: ContactRole[] = [
  { value: 'primary_contact', label: 'Primary Contact' },
  { value: 'secondary_contact', label: 'Secondary Contact' },
  { value: 'project_manager', label: 'Project Manager' },
  { value: 'technical_lead', label: 'Technical Lead' },
  { value: 'procurement_officer', label: 'Procurement Officer' },
  { value: 'finance_manager', label: 'Finance Manager' },
  { value: 'operations_manager', label: 'Operations Manager' },
  { value: 'legal_counsel', label: 'Legal Counsel' },
  { value: 'executive_sponsor', label: 'Executive Sponsor' },
  { value: 'stakeholder', label: 'Stakeholder' },
] as const;

export const MOCK_CONTACTS: Contact[] = [
  {
    id: '1',
    name: 'David Rodriguez',
    role: 'Primary Contact',
    email: 'david.rodriguez@losangelescounty.gov',
    phone: '(555) 123-4567',
    status: 'primary',
    accountId: 'acc-001',
    createdAt: '2024-01-10T08:00:00Z',
    updatedAt: '2024-01-10T08:00:00Z',
  },
  {
    id: '2',
    name: 'Sarah Johnson',
    role: 'Project Manager',
    email: 'sarah.johnson@losangelescounty.gov',
    phone: '(555) 234-5678',
    status: 'secondary',
    accountId: 'acc-001',
    createdAt: '2024-01-12T10:30:00Z',
    updatedAt: '2024-01-12T10:30:00Z',
  },
  {
    id: '3',
    name: 'Michael Chen',
    role: 'Technical Lead',
    email: 'michael.chen@losangelescounty.gov',
    phone: '(555) 345-6789',
    status: 'secondary',
    accountId: 'acc-001',
    createdAt: '2024-01-15T14:15:00Z',
    updatedAt: '2024-01-15T14:15:00Z',
  },
  {
    id: '4',
    name: 'Emily Davis',
    role: 'Finance Manager',
    email: 'emily.davis@losangelescounty.gov',
    phone: '(555) 456-7890',
    status: 'secondary',
    accountId: 'acc-001',
    createdAt: '2024-01-18T09:45:00Z',
    updatedAt: '2024-01-18T09:45:00Z',
  },
] as const;

export const DEFAULT_CONTACT_FORM_VALUES = {
  name: '',
  role: 'secondary_contact',
  email: '',
  phone: '',
} as const;
