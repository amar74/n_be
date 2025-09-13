import { z } from 'zod';

// Email validation regex
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Phone number validation (exactly 10 digits, no special characters)
const phoneRegex = /^[0-9]{10}$/;

// Postal code validation (supports various international formats)
const postalCodeRegex = /^[0-9]{5,6}$/;

export const CreateOrganizationSchema = z.object({
  name: z
    .string()
    .min(1, 'Organization name is required')
    .min(2, 'Organization name must be at least 2 characters')
    .max(100, 'Organization name must be less than 100 characters'),
  
  website: z
    .string()
    .optional()
    .refine((val) => {
      if (!val || val.trim() === '') return true; // Optional field
      // Allow URLs with or without protocol
      const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
      return urlPattern.test(val);
    }, 'Please enter a valid website URL'),
  
  address: z.object({
    line1: z.string().optional(),
    line2: z.string().optional(),
    city: z.string().optional(),
    pincode: z
      .number()
      .optional()
      .refine((val) => {
        if (val === undefined || val === null) return true; // Optional field
        return postalCodeRegex.test(val.toString());
      }, 'Please enter a valid postal code (5-6 digits)'),
  }).optional(),
  
  contact: z.object({
    email: z
      .string()
      .optional()
      .refine((val) => {
        if (!val || val.trim() === '') return true; // Optional field
        return emailRegex.test(val);
      }, 'Please enter a valid email address'),
    
    phone: z
      .string()
      .optional()
      .refine((val) => {
        if (!val || val.trim() === '') return true; // Optional field
        // Remove all non-digit characters for validation
        const cleanPhone = val.replace(/\D/g, '');
        return phoneRegex.test(cleanPhone);
      }, 'Please enter exactly 10 digits'),
  }).optional(),
}).refine((data) => {
  // At least one contact method should be provided if contact object exists
  if (data.contact && (data.contact.email || data.contact.phone)) {
    return true;
  }
  if (!data.contact || (!data.contact.email && !data.contact.phone)) {
    return true; // No contact is fine
  }
  return true;
}, {
  message: 'Please provide at least one contact method',
  path: ['contact'],
});

export type CreateOrganizationFormData = z.infer<typeof CreateOrganizationSchema>;
