import { z } from 'zod';
import { schemas } from '@/types/generated/accounts';
import { AccountCreate } from '@/types/accounts';

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

export const validateForm = (data: Partial<AccountCreate>): Record<string, string> => {
  const errors: Record<string, string> = {};
  
  try {
    createAccountSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.issues.forEach((err) => {
        if (err.path.length > 0) {
          errors[err.path[0] as string] = err.message;
        }
      });
    }
  }
  
  return errors;
};
