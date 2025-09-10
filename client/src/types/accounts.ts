import { z } from 'zod';
import { schemas } from './generated/accounts';

// Re-export base generated types
export type AccountCreate = z.infer<typeof schemas.AccountCreate>;
export type AccountUpdate = z.infer<typeof schemas.AccountUpdate>;
export type ContactCreate = z.infer<typeof schemas.ContactCreate>;
export type ContactResponse = z.infer<typeof schemas.ContactResponse>;
export type AddressCreate = z.infer<typeof schemas.AddressCreate>;
export type ClientType = z.infer<typeof schemas.ClientType>;

// Core contact interface
export interface Contact {
  name: string;
  email: string;
  phone: string;
  title?: string | null;
  contact_id: string;
}

// Address interface
export interface Address {
  line1: string;
  line2?: string | null;
  pincode?: number | null;
  address_id?: string;
}

// Consistent Account Detail Response - matches actual API response
export interface AccountDetailResponse {
  account_id: string;
  client_name: string;
  company_website?: string | null;
  client_address?: Address | null;
  primary_contact?: Contact | null;
  secondary_contacts?: Contact[];
  contact_email?: string | null;
  client_type: ClientType;
  market_sector?: string | null;
  notes?: string | null;
  total_value?: number | null;
  opportunities?: number | null;
  last_contact?: string | null;
  created_at?: string;
  updated_at?: string;
}

// Account List Item - for list views
export interface AccountListItem {
  account_id: string;
  client_name: string;
  company_website?: string | null;
  client_address?: Address | null;
  primary_contact?: Contact | null;
  client_type: ClientType;
  market_sector?: string | null;
  total_value?: number | null;
  ai_health_score?: number | null;
  last_contact?: string | null;
  created_at?: string;
  updated_at?: string;
}

// List response with pagination
export interface AccountListResponse {
  accounts: AccountListItem[];
  pagination: {
    total: number;
    page: number;
    size: number;
    has_prev: boolean;
    has_next: boolean;
  };
}

// Contacts API response
export interface ContactsResponse {
  contacts: Contact[];
}

// Form data interfaces for UI
export interface ContactFormData {
  name: string;
  email: string;
  phone: string;
  title?: string;
}

// Zod schema for contact form validation
export const contactFormSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  email: z
    .string()
    .email('Invalid email address')
    .max(255, 'Email must be less than 255 characters'),
  phone: z.string().min(1, 'Phone is required').max(20, 'Phone must be less than 20 characters'),
  title: z.string().max(100, 'Title must be less than 100 characters').optional(),
});

export type ContactFormValues = z.infer<typeof contactFormSchema>;

// Create account form data
export interface CreateAccountFormData {
  client_name: string;
  company_website?: string;
  client_address: {
    line1: string;
    line2?: string;
    pincode?: number;
  };
  client_type: ClientType;
  market_sector?: string;
  notes?: string;
  contacts?: ContactFormData[]; // First contact becomes primary, rest become secondary
}

// Update account form data
export interface UpdateAccountFormData {
  client_name?: string;
  company_website?: string;
  client_address?: {
    line1?: string;
    line2?: string;
    pincode?: number;
  };
  client_type?: ClientType;
  market_sector?: string;
  notes?: string;
}

// API Response types
export interface CreateAccountResponse {
  status_code: number;
  account_id: string;
  message: string;
}

export interface UpdateAccountResponse {
  status_code: number;
  message: string;
}

export interface DeleteAccountResponse {
  status_code: number;
  message: string;
}

export interface CreateContactResponse {
  status_code: number;
  contact_id: string;
  message: string;
}

export interface UpdateContactResponse {
  status_code: number;
  message: string;
}

export interface DeleteContactResponse {
  status_code: number;
  message: string;
}

// Client tier options
export const CLIENT_TIERS: { value: ClientType; label: string; description: string }[] = [
  { value: 'tier_1', label: 'Tier 1', description: 'Premium clients with full access' },
  { value: 'tier_2', label: 'Tier 2', description: 'Standard clients with regular features' },
  { value: 'tier_3', label: 'Tier 3', description: 'Basic clients with limited features' },
];

// Industry/Market sector options
export const MARKET_SECTORS = [
  'Technology',
  'Healthcare',
  'Finance',
  'Manufacturing',
  'Retail',
  'Education',
  'Real Estate',
  'Consulting',
  'Legal',
  'Marketing',
  'Construction',
  'Transportation',
  'Energy',
  'Food & Beverage',
  'Other',
];
