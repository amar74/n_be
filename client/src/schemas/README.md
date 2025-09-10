# Schemas Documentation

This directory contains data validation schemas and form validation logic for the Megapolis application.

## Purpose

- Define data validation rules and schemas
- Provide consistent validation across forms and API endpoints
- Centralize validation logic for reusability
- Ensure data integrity and type safety

## Validation Libraries

The application uses modern validation libraries for schema definition:

- **Zod**: Runtime type validation and schema definition
- **React Hook Form**: Form state management with validation integration
- **Custom Validators**: Application-specific validation rules

## Schema Categories

### Authentication Schemas

Validation schemas for authentication forms and API requests.

```typescript
// auth.schemas.ts
import { z } from 'zod';

export const LoginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format')
    .max(255, 'Email is too long'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

export const SignupSchema = z
  .object({
    email: z
      .string()
      .min(1, 'Email is required')
      .email('Invalid email format')
      .max(255, 'Email is too long'),
    password: z
      .string()
      .min(6, 'Password must be at least 6 characters')
      .max(100, 'Password is too long'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

export const ResetPasswordSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email format'),
});

// Type inference from schemas
export type LoginFormData = z.infer<typeof LoginSchema>;
export type SignupFormData = z.infer<typeof SignupSchema>;
export type ResetPasswordFormData = z.infer<typeof ResetPasswordSchema>;
```

### User Data Schemas

Schemas for user profile and management operations.

```typescript
// user.schemas.ts
import { z } from 'zod';

export const UserProfileSchema = z.object({
  id: z.number().positive(),
  email: z.string().email(),
  name: z.string().min(1).max(100).optional(),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

export const UpdateProfileSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name is too long').optional(),
  email: z.string().email('Invalid email format').max(255, 'Email is too long').optional(),
});

export type User = z.infer<typeof UserProfileSchema>;
export type UpdateProfileData = z.infer<typeof UpdateProfileSchema>;
```

### API Response Schemas

Validation schemas for API responses and requests.

```typescript
// api.schemas.ts
import { z } from 'zod';

export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    data: dataSchema,
    message: z.string().optional(),
    success: z.boolean(),
  });

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    data: z.array(itemSchema),
    total: z.number().nonnegative(),
    page: z.number().positive(),
    limit: z.number().positive(),
    totalPages: z.number().nonnegative(),
  });

export const ErrorResponseSchema = z.object({
  message: z.string(),
  code: z.string().optional(),
  details: z.record(z.any()).optional(),
});
```

## Form Integration

### React Hook Form Integration

Schemas integrate seamlessly with React Hook Form using resolvers.

```typescript
// Using schemas with React Hook Form
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { LoginSchema, LoginFormData } from '../schemas/auth.schemas'

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginFormData>({
    resolver: zodResolver(LoginSchema)
  })

  const onSubmit = async (data: LoginFormData) => {
    // Form data is automatically validated
    await authService.login(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email')}
        type="email"
        placeholder="Email"
      />
      {errors.email && <span>{errors.email.message}</span>}

      <input
        {...register('password')}
        type="password"
        placeholder="Password"
      />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Signing in...' : 'Sign in'}
      </button>
    </form>
  )
}
```

### API Validation

Schemas can validate API responses for type safety.

```typescript
// API service with response validation
import { UserProfileSchema } from '../schemas/user.schemas';

export const userService = {
  async getProfile(): Promise<User> {
    const response = await apiClient.get('/auth/me');

    // Validate response data
    const result = UserProfileSchema.safeParse(response.data.user);

    if (!result.success) {
      throw new Error('Invalid user data received from server');
    }

    return result.data;
  },
};
```

## Custom Validators

### Business Logic Validators

Application-specific validation rules.

```typescript
// custom.validators.ts
import { z } from 'zod';

// Custom email domain validator
export const businessEmailValidator = z
  .string()
  .email()
  .refine(
    email => !email.endsWith('@gmail.com') && !email.endsWith('@yahoo.com'),
    'Business email required'
  );

// Password strength validator
export const strongPasswordValidator = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character');

// Phone number validator
export const phoneNumberValidator = z
  .string()
  .regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format');
```

## File Organization

### Structure

```
schemas/
├── index.ts          # Main exports
├── auth.schemas.ts   # Authentication validation
├── user.schemas.ts   # User data validation
├── api.schemas.ts    # API response validation
├── form.schemas.ts   # Common form validation
└── custom.validators.ts # Custom validation rules
```

### Export Strategy

```typescript
// schemas/index.ts
export * from './auth.schemas';
export * from './user.schemas';
export * from './api.schemas';
export * from './form.schemas';
export * from './custom.validators';
```

## Best Practices

1. **Schema Composition**: Build complex schemas from simpler ones
2. **Error Messages**: Provide clear, user-friendly error messages
3. **Type Inference**: Use `z.infer<>` for automatic type generation
4. **Reusability**: Create reusable schema components
5. **Testing**: Test validation schemas with edge cases
6. **Performance**: Consider schema parsing performance for large forms
7. **Documentation**: Document complex validation rules

## Advanced Patterns

### Conditional Validation

```typescript
const ConditionalSchema = z
  .object({
    type: z.enum(['personal', 'business']),
    email: z.string().email(),
    businessName: z.string().optional(),
  })
  .refine(data => data.type !== 'business' || data.businessName, {
    message: 'Business name is required for business accounts',
    path: ['businessName'],
  });
```

### Transform and Preprocess

```typescript
const PreprocessedSchema = z.object({
  email: z.string().transform(email => email.toLowerCase().trim()),
  age: z
    .string()
    .transform(val => parseInt(val, 10))
    .pipe(z.number().min(18)),
});
```

### Async Validation

```typescript
const AsyncValidationSchema = z
  .object({
    email: z.string().email(),
  })
  .refine(async data => {
    // Check if email is already taken
    const exists = await checkEmailExists(data.email);
    return !exists;
  }, 'Email is already registered');
```
