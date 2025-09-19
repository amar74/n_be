import { Tab, RecentActivityItem } from './AccountDetailsPage.types';

export const ACCOUNT_DETAILS_TABS: Tab[] = [
  {
    id: 'overview',
    label: 'Overview',
    icon: 'LayoutDashboard',
  },
  {
    id: 'contacts',
    label: 'Contacts',
    icon: 'Users',
  },
  {
    id: 'team',
    label: 'Team',
    icon: 'UserCheck',
  },
  {
    id: 'opportunities',
    label: 'Opportunities',
    icon: 'Target',
  },
  {
    id: 'experience',
    label: 'Experience',
    icon: 'Star',
  },
  {
    id: 'performance',
    label: 'Performance',
    icon: 'BarChart3',
  },
  {
    id: 'notes',
    label: 'Notes',
    icon: 'FileText',
  },
  {
    id: 'financial',
    label: 'Financial',
    icon: 'DollarSign',
  },
] as const;

export const MOCK_RECENT_ACTIVITY: RecentActivityItem[] = [
  {
    id: '1',
    title: 'Proposal submitted for metro transit expansion',
    timestamp: '2 days ago',
    icon: 'FileText',
    color: '#22c55e',
  },
  {
    id: '2',
    title: 'Meeting with Sarah Johnson scheduled',
    timestamp: '1 week ago',
    icon: 'Calendar',
    color: '#3b82f6',
  },
  {
    id: '3',
    title: 'Contract amendment signed',
    timestamp: '2 weeks ago',
    icon: 'CheckCircle',
    color: '#8b5cf6',
  },
] as const;

export const CLIENT_TYPES = [
  { value: 'tier_1', label: 'Tier 1' },
  { value: 'tier_2', label: 'Tier 2' },
  { value: 'tier_3', label: 'Tier 3' },
] as const;

export const US_STATES = [
  { value: 'AL', label: 'Alabama' },
  { value: 'AK', label: 'Alaska' },
  { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' },
  { value: 'CA', label: 'California' },
  { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' },
  { value: 'DE', label: 'Delaware' },
  { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' },
  // Add more states as needed
] as const;

export const FORM_FIELD_LABELS = {
  client_name: 'Client Name',
  client_type: 'Client Type',
  market_sector: 'Market Sector',
  client_address: 'Address',
  city: 'City',
  state: 'State',
  zip_code: 'Zip Code',
  company_website: 'Website',
  hosting_area: 'Hosting Area',
  msa_in_place: 'MSA in Place',
  account_approver: 'Account Approver',
  approval_date_time: 'Approval Date & Time',
} as const;

