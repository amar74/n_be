import { z } from 'zod';
import { schemas } from './generated/auth';

// Re-export generated types
// Note: Backend returns user object directly, not wrapped in { user: ... }
export type CurrentUserResponse = z.infer<typeof schemas.CurrentUserResponse>;
export type CurrentUser = CurrentUserResponse['user']; // Extract the user part
export type SignupSuccess = z.infer<typeof schemas.OnSignupSuccessResponse>;
export type SignupError = z.infer<typeof schemas.OnSignupErrorResponse>;

// Business logic extensions
export interface AuthState {
  user: CurrentUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginFormData extends LoginCredentials {
  rememberMe?: boolean;
}

export interface SignupCredentials {
  email: string;
  password: string;
  confirmPassword: string;
  name?: string;
}

export interface ResetPasswordRequest {
  email: string;
}

export interface UpdatePasswordRequest {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}

export interface ResetPasswordFormRequest {
  newPassword: string;
  confirmPassword: string;
}

// User role extensions
export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  MANAGER = 'manager',
  VIEWER = 'viewer',
}

export interface AuthUserExtended extends CurrentUser {
  displayName?: string;
  isActive: boolean;
  lastLoginAt?: string;
  permissions?: string[];
}

// Auth context types
export interface AuthContextValue {
  state: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (credentials: SignupCredentials) => Promise<void>;
  logout: () => void;
  resetPassword: (request: ResetPasswordRequest) => Promise<void>;
  updatePassword: (request: UpdatePasswordRequest) => Promise<void>;
  refreshUser: () => Promise<void>;
}

// Auth response types for better error handling
export interface AuthResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export type LoginResponse = AuthResponse<{ user: CurrentUser; token: string }>;
export type LogoutResponse = AuthResponse<{ message: string }>;

// Zod validation schemas for forms
export const LoginFormSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(6, 'Password must be at least 6 characters'),
  rememberMe: z.boolean().optional(),
});

export const SignupFormSchema = z
  .object({
    email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
    password: z
      .string()
      .min(1, 'Password is required')
      .min(8, 'Password must be at least 8 characters')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        'Password must contain at least one uppercase letter, one lowercase letter, and one number'
      ),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
    name: z.string().optional(),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export const ResetPasswordFormSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
});

export const UpdatePasswordFormSchema = z
  .object({
    currentPassword: z.string().min(1, 'Current password is required'),
    newPassword: z
      .string()
      .min(1, 'New password is required')
      .min(8, 'Password must be at least 8 characters')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        'Password must contain at least one uppercase letter, one lowercase letter, and one number'
      ),
    confirmPassword: z.string().min(1, 'Please confirm your new password'),
  })
  .refine(data => data.newPassword === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export const ResetPasswordNewFormSchema = z
  .object({
    newPassword: z
      .string()
      .min(1, 'New password is required')
      .min(6, 'Password must be at least 6 characters'),
    confirmPassword: z.string().min(1, 'Please confirm your new password'),
  })
  .refine(data => data.newPassword === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });
