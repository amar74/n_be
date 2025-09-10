# Utils Documentation

This directory contains utility functions and helper modules for the Megapolis application.

## Purpose

- Provide reusable utility functions across the application
- Centralize common operations and calculations
- Offer type-safe helper functions
- Reduce code duplication

## Utility Categories

### Data Manipulation

Functions for transforming and processing data.

```typescript
// formatters.ts
export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

export const formatDate = (date: Date | string, format = 'short'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: format as 'short' | 'medium' | 'long',
  }).format(dateObj);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
};
```

### Validation Helpers

Utility functions for data validation.

```typescript
// validation.ts
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPassword = (password: string): boolean => {
  return password.length >= 6;
};

export const validateRequired = (value: any): boolean => {
  if (typeof value === 'string') return value.trim().length > 0;
  return value !== null && value !== undefined;
};
```

### Storage Utilities

Functions for localStorage and sessionStorage operations.

```typescript
// storage.ts
export const setLocalStorage = <T>(key: string, value: T): void => {
  try {
    const serializedValue = JSON.stringify(value);
    localStorage.setItem(key, serializedValue);
  } catch (error) {
    console.error('Error saving to localStorage:', error);
  }
};

export const getLocalStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error('Error reading from localStorage:', error);
    return defaultValue;
  }
};

export const removeLocalStorage = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing from localStorage:', error);
  }
};
```

### Performance Utilities

Functions for optimization and performance.

```typescript
// performance.ts
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

export const memoize = <T extends (...args: any[]) => any>(func: T): T => {
  const cache = new Map();
  return ((...args: Parameters<T>) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = func(...args);
    cache.set(key, result);
    return result;
  }) as T;
};
```

### Error Handling

Utilities for error processing and reporting.

```typescript
// errors.ts
export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

export const logError = (error: Error, context?: string): void => {
  console.error(`[${context || 'Error'}]:`, error);

  // In production, send to error tracking service
  if (import.meta.env.PROD) {
    // sendToErrorTracking(error, context)
  }
};
```

### URL and Navigation

Helper functions for URL manipulation and navigation.

```typescript
// navigation.ts
export const buildUrl = (base: string, params?: Record<string, string | number>): string => {
  if (!params) return base;

  const url = new URL(base, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    url.searchParams.set(key, String(value));
  });
  return url.toString();
};

export const getUrlParam = (name: string): string | null => {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
};

export const removeUrlParam = (name: string): void => {
  const url = new URL(window.location.href);
  url.searchParams.delete(name);
  window.history.replaceState({}, '', url.toString());
};
```

## File Organization

### Structure

```
utils/
├── index.ts          # Main exports
├── formatters.ts     # Data formatting functions
├── validation.ts     # Validation helpers
├── storage.ts        # LocalStorage utilities
├── performance.ts    # Debounce, throttle, memoize
├── errors.ts         # Error handling utilities
├── navigation.ts     # URL and routing helpers
└── constants.ts      # Application constants
```

### Export Strategy

```typescript
// utils/index.ts
export * from './formatters';
export * from './validation';
export * from './storage';
export * from './performance';
export * from './errors';
export * from './navigation';
export * from './constants';
```

## Constants

Application-wide constants and configuration values.

```typescript
// constants.ts
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    SIGNUP: '/auth/signup',
    VERIFY_TOKEN: '/auth/verify_supabase_token',
    ME: '/auth/me',
  },
  USERS: '/api/users',
  ACCOUNTS: '/api/accounts',
} as const;

export const STORAGE_KEYS = {
  JWT_TOKEN: 'jwtToken',
  SUPABASE_TOKEN: 'supabaseToken',
  USER_INFO: 'userInfo',
  THEME: 'theme',
} as const;

export const VALIDATION_RULES = {
  PASSWORD_MIN_LENGTH: 6,
  EMAIL_MAX_LENGTH: 255,
  NAME_MAX_LENGTH: 100,
} as const;
```

## Usage Examples

### In Components

```typescript
import { formatDate, debounce, validateRequired } from '../utils'

function UserProfile({ user }) {
  const [searchTerm, setSearchTerm] = useState('')

  const debouncedSearch = debounce((term: string) => {
    // Perform search
  }, 300)

  return (
    <div>
      <p>Joined: {formatDate(user.created_at)}</p>
      <input
        onChange={(e) => {
          setSearchTerm(e.target.value)
          debouncedSearch(e.target.value)
        }}
        required={validateRequired(searchTerm)}
      />
    </div>
  )
}
```

### In Services

```typescript
import { handleApiError, logError } from '../utils';

export const userService = {
  async getUser(id: number) {
    try {
      const response = await apiClient.get(`/users/${id}`);
      return response.data;
    } catch (error) {
      const message = handleApiError(error);
      logError(error, 'userService.getUser');
      throw new Error(message);
    }
  },
};
```

## Best Practices

1. **Pure Functions**: Make utility functions pure when possible
2. **Type Safety**: Include proper TypeScript types for all utilities
3. **Error Handling**: Handle edge cases and provide fallbacks
4. **Performance**: Consider performance implications of utility functions
5. **Testing**: Write unit tests for utility functions
6. **Documentation**: Include JSDoc comments for complex utilities
7. **Tree Shaking**: Structure exports to support tree shaking
