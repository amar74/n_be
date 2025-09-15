export const MARKET_SECTORS = [
  'Transportation',
  'Infrastructure', 
  'Environmental',
  'Aviation',
  'Education',
  'Healthcare',
  'Government',
] as const;

export const CLIENT_TYPES = ['Tire 1', 'Tire 2', 'Tire 3'] as const;

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
] as const;

export const INITIAL_FORM_DATA = {
  companyWebsite: '',
  clientName: '',
  clientAddress1: '',
  clientAddress2: '',
  city: '',
  state: '',
  zipCode: '',
  primaryContact: '',
  contactEmail: '',
  clientMarketSector: '',
  clientType: '',
  hostingArea: '',
  msaInPlace: '',
};
