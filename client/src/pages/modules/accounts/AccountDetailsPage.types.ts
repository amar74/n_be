import { AccountDetailResponse } from '@/types/accounts';

export type TabType = 
  | 'overview'
  | 'contacts'
  | 'team'
  | 'opportunities'
  | 'experience'
  | 'performance'
  | 'notes'
  | 'financial';

export interface Tab {
  id: TabType;
  label: string;
  icon: string;
}

export interface AccountStatsCard {
  id: string;
  title: string;
  value: string | number;
  icon: string;
  color?: string;
}

export interface RecentActivityItem {
  id: string;
  title: string;
  timestamp: string;
  icon: string;
  color?: string;
}

export interface AccountFormData {
  client_name: string;
  client_type: string;
  market_sector: string;
  client_address_line1: string;
  client_address_line2?: string | null;
  client_address_city?: string | null;
  client_address_state?: string | null;
  client_address_zip_code?: string | null;
  company_website: string;
  hosting_area: string;
  msa_in_place: boolean;
  account_approver?: string;
  approval_date_time?: string;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface AccountDetailsState {
  account: AccountDetailResponse | null;
  isLoading: boolean;
  isEditing: boolean;
  activeTab: TabType;
  formData: AccountFormData | null;
}

