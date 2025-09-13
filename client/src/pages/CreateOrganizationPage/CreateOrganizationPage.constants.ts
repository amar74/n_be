export const FORM_DEFAULT_VALUES = {
  name: '',
  website: '',
  address: {
    line1: '',
    line2: '',
    city: '',
    pincode: undefined,
  },
  contact: {
    email: '',
    phone: '',
  },
};

export const WEBSITE_ANALYSIS_DELAY = 1500; // milliseconds

export const STEPS = {
  ORGANIZATION_SETUP: {
    number: 1,
    title: 'Organization Setup',
  },
  PLATFORM_ACCESS: {
    number: 2,
    title: 'Platform Access',
  },
} as const;
