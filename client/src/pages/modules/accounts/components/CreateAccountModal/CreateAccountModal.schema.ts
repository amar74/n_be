import { z } from 'zod';
import { schemas } from '@/types/generated/accounts';
import { AccountCreate } from '@/types/accounts';
import { UIAccountFormData } from './CreateAccountModal.types';

// Validation regex patterns
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
const postalCodeRegex = /^[0-9]{5,6}$/;

// Enhanced validation schema for UI form data
export const createAccountUISchema = z.object({
  client_name: z
    .string()
    .min(1, 'Client name is required')
    .min(2, 'Client name must be at least 2 characters')
    .max(100, 'Client name must be less than 100 characters'),
  
  company_website: z
    .union([z.string(), z.null()])
    .optional()
    .refine((val) => {
      if (!val || val === null || val.trim() === '') return true; // Optional field
      // Allow URLs with or without protocol
      const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/i;
      return urlPattern.test(val);
    }, 'Please enter a valid website URL'),
  
  client_address: z.object({
    line1: z
      .string()
      .min(1, 'Address line 1 is required')
      .max(200, 'Address line 1 must be less than 200 characters'),
    line2: z
      .union([z.string(), z.null()])
      .optional()
      .refine((val) => {
        if (!val || val === null || val.trim() === '') return true;
        return val.length <= 200;
      }, 'Address line 2 must be less than 200 characters'),
    city: z
      .union([z.string(), z.null()])
      .optional()
      .refine((val) => {
        if (!val || val === null || val.trim() === '') return true;
        return val.length >= 2 && val.length <= 100;
      }, 'City must be between 2 and 100 characters'),
    state: z.union([z.string(), z.null()]).optional(), // UI-only field
    pincode: z
      .union([z.number(), z.null()])
      .optional()
      .refine((val) => {
        if (val === undefined || val === null) return true; // Optional field
        return postalCodeRegex.test(val.toString());
      }, 'Please enter a valid postal code (5-6 digits)'),
  }),
  
  primary_contact: z.object({
    name: z
      .string()
      .min(1, 'Primary contact name is required')
      .min(2, 'Contact name must be at least 2 characters')
      .max(100, 'Contact name must be less than 100 characters'),
    
    email: z
      .string()
      .min(1, 'Primary contact email is required')
      .refine((val) => {
        return emailRegex.test(val);
      }, 'Please enter a valid email address'),
    
    phone: z
      .string()
      .min(1, 'Primary contact phone is required')
      .refine((val) => {
        // Remove spaces, dashes, and parentheses for validation
        const cleanPhone = val.replace(/[\s\-\(\)]/g, '');
        return phoneRegex.test(cleanPhone);
      }, 'Please enter a valid phone number'),
    
    title: z.union([z.string(), z.null()]).optional(),
  }),
  
  secondary_contacts: z.array(z.object({
    name: z
      .string()
      .min(1, 'Contact name is required')
      .min(2, 'Contact name must be at least 2 characters')
      .max(100, 'Contact name must be less than 100 characters'),
    
    email: z
      .string()
      .min(1, 'Contact email is required')
      .refine((val) => {
        return emailRegex.test(val);
      }, 'Please enter a valid email address'),
    
    phone: z
      .string()
      .min(1, 'Contact phone is required')
      .refine((val) => {
        // Remove spaces, dashes, and parentheses for validation
        const cleanPhone = val.replace(/[\s\-\(\)]/g, '');
        return phoneRegex.test(cleanPhone);
      }, 'Please enter a valid phone number'),
    
    title: z.union([z.string(), z.null()]).optional(),
  })).optional(),
  
  client_type: z.enum(['tier_1', 'tier_2', 'tier_3']),
  
  market_sector: z.union([z.string(), z.null()]).optional(),
  notes: z.union([z.string(), z.null()]).optional(),
});

// Use the generated schema for backend validation
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
  
  try {
    createAccountUISchema.parse(data);
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
