import { z } from 'zod';
import { schemas } from '@/types/generated/accounts';
import { AccountCreate } from '@/types/accounts';
import { UIAccountFormData } from './CreateAccountModal.types';

export const createAccountSchema = schemas.AccountCreate;

export const validateField = (field: keyof AccountCreate, value: any): string | null => {
  try {
    // Type-safe field access
    const schema = createAccountSchema.shape[field as keyof typeof createAccountSchema.shape];
    if (!schema) {
      return 'Invalid field';
    }
    
    // Parse the value
    schema.parse(value);
    return null;
  } catch (error) {
    if (error instanceof z.ZodError) {
      return error.issues[0]?.message || 'Invalid value';
    }
    return 'Invalid value';
  }
};

export const validateForm = (data: UIAccountFormData): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  // Strip the state field from client_address before validation
  const { state, ...addressWithoutState } = data.client_address;
  const backendData: AccountCreate = {
    ...data,
    client_address: addressWithoutState,
  };
  
  try {
    createAccountSchema.parse(backendData);
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.issues.forEach((err) => {
        if (err.path.length > 0) {
          const path = err.path.join('.');
          errors[path] = err.message;
        }
      });
    }
  }
  
  return errors;
};
