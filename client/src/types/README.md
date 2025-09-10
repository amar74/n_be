# Types Documentation

This directory contains TypeScript type definitions and interfaces for the Megapolis application.

## Purpose

- Centralize all TypeScript type definitions
- Ensure type safety across the application
- Provide reusable interfaces for API data structures
- Document data shapes and contracts

## Type Categories

### Authentication Types

User authentication and session related types.

```typescript
// User data from backend API
export interface User {
  id: number
  email: string
  name?: string
  created_at?: string
  updated_at?: string
}

// Supabase user type (imported from @supabase/supabase-js)
export type SupabaseUser = User as SupabaseUserType

// Authentication state
export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}
```

### API Types

Request and response interfaces for API endpoints.

```typescript
// Standard API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

// Error response structure
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// Pagination parameters
export interface PaginationParams {
  page: number;
  limit: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

// Paginated response
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
```

### Form Types

Form data and validation interfaces.

```typescript
// Login form data
export interface LoginFormData {
  email: string;
  password: string;
}

// Registration form data
export interface SignupFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

// Password reset form data
export interface ResetPasswordFormData {
  email: string;
}
```

### Component Props

Common component prop interfaces.

```typescript
// Generic loading component props
export interface LoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

// Error display component props
export interface ErrorProps {
  message: string;
  onRetry?: () => void;
}

// Modal component props
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}
```

## Type Organization

### File Structure

```
types/
├── index.ts          # Main exports
├── auth.types.ts     # Authentication types
├── api.types.ts      # API response types
├── user.types.ts     # User-related types
├── form.types.ts     # Form data types
└── component.types.ts # Component prop types
```

### Export Strategy

```typescript
// types/index.ts
export * from './auth.types';
export * from './api.types';
export * from './user.types';
export * from './form.types';
export * from './component.types';

// Usage in components
import { User, ApiResponse } from '../types';
```

## Best Practices

1. **Naming Conventions**: Use PascalCase for interfaces and types
2. **Optional Properties**: Use `?` for optional fields
3. **Generic Types**: Use generics for reusable type patterns
4. **Enum Usage**: Define enums for fixed value sets
5. **Union Types**: Use union types for limited string/number values
6. **Documentation**: Include JSDoc comments for complex types

## Common Patterns

### Generic API Response

```typescript
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
  errors?: Record<string, string[]>;
}

// Usage
const userResponse: ApiResponse<User> = await api.getUser(id);
const usersResponse: ApiResponse<User[]> = await api.getUsers();
```

### Form State Types

```typescript
export interface FormState<T> {
  data: T;
  errors: Partial<Record<keyof T, string>>;
  loading: boolean;
  touched: Partial<Record<keyof T, boolean>>;
}

// Usage
const [formState, setFormState] = useState<FormState<LoginFormData>>({
  data: { email: '', password: '' },
  errors: {},
  loading: false,
  touched: {},
});
```

### Redux State Types

```typescript
export interface BaseSliceState<T> {
  data: T[];
  currentItem: T | null;
  loading: boolean;
  error: string | null;
}

// Usage
export interface UsersState extends BaseSliceState<User> {
  filters: UserFilters;
  pagination: PaginationState;
}
```

## Integration with External Libraries

### Supabase Types

```typescript
import type { User as SupabaseUser } from '@supabase/supabase-js';

// Extend or adapt Supabase types
export interface ExtendedUser extends SupabaseUser {
  backendId?: number;
  preferences?: UserPreferences;
}
```

### React Router Types

```typescript
// Route parameter types
export interface UserRouteParams {
  userId: string;
}

// Location state types
export interface NavigationState {
  from?: string;
  returnTo?: string;
}
```

## Type Guards

Utility functions for runtime type checking:

```typescript
// Type guard for User objects
export function isUser(obj: any): obj is User {
  return obj && typeof obj.id === 'number' && typeof obj.email === 'string';
}

// Type guard for API errors
export function isApiError(obj: any): obj is ApiError {
  return obj && typeof obj.message === 'string';
}
```
