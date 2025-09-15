import { z } from 'zod';
import { MARKET_SECTORS, CLIENT_TYPES, HOSTING_AREAS, MSA_OPTIONS, US_STATES } from './CreateAccountModal.constants';

export const createAccountSchema = z.object({
  companyWebsite: z.string().default(''),
  clientName: z.string().min(1, 'Client Name is required').trim(),
  clientAddress1: z.string().min(1, 'Client Address 1 is required').trim(),
  clientAddress2: z.string().default(''),
  city: z.string().min(1, 'City is required').trim(),
  state: z.string().min(1, 'State is required'),
  zipCode: z.string().default(''),
  primaryContact: z.string().default(''),
  contactEmail: z.string().refine((val) => val === '' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val), 'Please enter a valid email address').default(''),
  clientMarketSector: z.string().min(1, 'Client Market Sector is required'),
  clientType: z.string().min(1, 'Client Type is required'),
  hostingArea: z.string().default(''),
  msaInPlace: z.string().default(''),
});

export type CreateAccountFormData = z.infer<typeof createAccountSchema>;

export const validateField = (field: keyof CreateAccountFormData, value: any): string | null => {
  try {
    const fieldSchema = createAccountSchema.shape[field];
    fieldSchema.parse(value);
    return null;
  } catch (error) {
    if (error instanceof z.ZodError) {
      return error.errors[0]?.message || 'Invalid value';
    }
    return 'Invalid value';
  }
};

export const validateForm = (data: Partial<CreateAccountFormData>): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  try {
    createAccountSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.errors.forEach((err) => {
        if (err.path.length > 0) {
          errors[err.path[0] as string] = err.message;
        }
      });
    }
  }
  
  return errors;
};
