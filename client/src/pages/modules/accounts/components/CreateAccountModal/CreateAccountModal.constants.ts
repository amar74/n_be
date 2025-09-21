import { ClientType } from './CreateAccountModal.types';

export const MARKET_SECTORS = [
  'Transportation',
  'Infrastructure', 
  'Environmental',
  'Aviation',
  'Education',
  'Healthcare',
  'Government',
] as const;


export const CLIENT_TYPES = Object.values(ClientType);

export const CLIENT_TYPE_DISPLAY: Record<ClientType, string> = {
  [ClientType.TIER_1]: 'Tier 1',
  [ClientType.TIER_2]: 'Tier 2',
  [ClientType.TIER_3]: 'Tier 3',
} as const;

export const HOSTING_AREAS = [
  'Northeast Office',
  'Southeast Office', 
  'Midwest Office',
  'Southwest Office',
  'West Office',
] as const;

export const MSA_OPTIONS = ['Yes', 'No'] as const;

export const US_STATES = [
  'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
  'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
  'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
  'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
  'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
  'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
  'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
];

export const WEBSITE_ANALYSIS_DELAY = 1500; // milliseconds

export const INITIAL_FORM_DATA = {
  client_name: '',
  company_website: null,
  client_address: {
    line1: '',
    line2: null,
    city: null,
    state: null, // UI-only field for state dropdown
    pincode: null,
  },
  primary_contact: {
    name: '',
    email: '',
    phone: '',
    title: null,
  },
  secondary_contacts: [],
  client_type: 'tier_1' as const,
  market_sector: null,
  notes: null,
};
