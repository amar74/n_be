# Features Documentation

This directory contains feature-based modules and components for the Megapolis application.

## Purpose

- Organize code by business features rather than technical layers
- Encapsulate related components, services, and logic together
- Promote feature independence and reusability
- Enable easier testing and maintenance of business logic

## Feature-Based Architecture

### Structure Pattern

Each feature should follow this organizational pattern:

```
features/
├── authentication/
│   ├── components/
│   │   ├── LoginForm.tsx
│   │   ├── SignupForm.tsx
│   │   └── PasswordResetForm.tsx
│   ├── hooks/
│   │   ├── useAuthForm.ts
│   │   └── usePasswordValidation.ts
│   ├── services/
│   │   └── auth.service.ts
│   ├── types/
│   │   └── auth.types.ts
│   └── index.ts
├── user-management/
│   ├── components/
│   │   ├── UserList.tsx
│   │   ├── UserCard.tsx
│   │   └── UserModal.tsx
│   ├── hooks/
│   │   └── useUserData.ts
│   ├── services/
│   │   └── users.service.ts
│   └── index.ts
└── accounts/
    ├── components/
    ├── hooks/
    ├── services/
    └── index.ts
```

## Feature Guidelines

### Feature Boundaries

- **Self-Contained**: Each feature should be as independent as possible
- **Clear Interface**: Export only necessary components and functions
- **Minimal Dependencies**: Reduce cross-feature dependencies
- **Shared Resources**: Use shared utilities, types, and services appropriately

### Feature Composition

```typescript
// features/authentication/index.ts
export { LoginForm, SignupForm } from './components';
export { useAuthForm } from './hooks';
export { authService } from './services';
export type { LoginFormData, SignupFormData } from './types';

// Usage in pages
import { LoginForm } from '../features/authentication';
```

## Example Features

### Authentication Feature

Complete authentication functionality encapsulated in one feature.

```typescript
// features/authentication/components/LoginForm.tsx
import { useAuthForm } from '../hooks/useAuthForm'
import { LoginFormData } from '../types/auth.types'

export function LoginForm() {
  const { handleLogin, loading, error } = useAuthForm()

  const onSubmit = async (data: LoginFormData) => {
    await handleLogin(data)
  }

  return (
    // Login form implementation
  )
}

// features/authentication/hooks/useAuthForm.ts
import { useState } from 'react'
import { authService } from '../services/auth.service'

export function useAuthForm() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (data: LoginFormData) => {
    setLoading(true)
    try {
      await authService.login(data)
      // Handle success
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return { handleLogin, loading, error }
}
```

### User Management Feature

User-related functionality grouped together.

```typescript
// features/user-management/components/UserList.tsx
import { useUserData } from '../hooks/useUserData'
import { UserCard } from './UserCard'

export function UserList() {
  const { users, loading, error, refreshUsers } = useUserData()

  if (loading) return <div>Loading users...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div className="user-list">
      {users.map(user => (
        <UserCard key={user.id} user={user} onUpdate={refreshUsers} />
      ))}
    </div>
  )
}

// features/user-management/hooks/useUserData.ts
import { useState, useEffect } from 'react'
import { userService } from '../services/users.service'

export function useUserData() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchUsers = async () => {
    try {
      const data = await userService.getAll()
      setUsers(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  return {
    users,
    loading,
    error,
    refreshUsers: fetchUsers
  }
}
```

## Feature Integration

### Cross-Feature Communication

When features need to communicate, use these patterns:

```typescript
// Shared events/hooks
export const useFeatureEvents = () => {
  const { user } = useAuth() // Shared auth state
  const dispatch = useAppDispatch() // Shared Redux actions

  return {
    onUserUpdate: (user) => dispatch(updateUser(user)),
    onLogout: () => dispatch(clearUser())
  }
}

// Feature composition in pages
function Dashboard() {
  return (
    <div>
      <UserProfile /> {/* From user-management feature */}
      <AccountsList /> {/* From accounts feature */}
      <RecentActivity /> {/* From activity feature */}
    </div>
  )
}
```

### Shared Dependencies

Features can depend on shared resources:

```typescript
// features/accounts/services/accounts.service.ts
import { apiClient } from '../../services/api/client'; // Shared API client
import { handleApiError } from '../../utils/errors'; // Shared utilities

export const accountsService = {
  async getAccounts() {
    try {
      const response = await apiClient.get('/api/accounts');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};
```

## Testing Features

### Feature Testing Strategy

```typescript
// features/authentication/__tests__/LoginForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { LoginForm } from '../components/LoginForm'

describe('LoginForm', () => {
  it('should handle login submission', async () => {
    render(<LoginForm />)

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    })

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))

    // Assert expected behavior
  })
})
```

## Best Practices

1. **Feature Cohesion**: Keep related functionality together
2. **Clear Interfaces**: Export only what other features need
3. **Dependency Management**: Minimize cross-feature dependencies
4. **Testing**: Test features in isolation when possible
5. **Documentation**: Document feature APIs and dependencies
6. **Consistency**: Follow consistent patterns across features
7. **Performance**: Consider code splitting at the feature level

## Migration Strategy

### Converting to Feature-Based

When refactoring existing code to feature-based architecture:

1. **Identify Features**: Group related components and logic
2. **Extract Common Code**: Move shared utilities to appropriate places
3. **Update Imports**: Change import paths to use feature exports
4. **Test Integration**: Ensure features work together correctly
5. **Document Changes**: Update documentation for new structure

### Example Migration

```typescript
// Before: scattered across directories
// components/LoginForm.tsx
// services/auth.service.ts
// hooks/useAuth.ts

// After: organized by feature
// features/authentication/
//   ├── components/LoginForm.tsx
//   ├── services/auth.service.ts
//   ├── hooks/useAuth.ts
//   └── index.ts

// Update imports
// Before:
import LoginForm from '../components/LoginForm';

// After:
import { LoginForm } from '../features/authentication';
```

## Future Features

Consider these patterns when adding new features:

- **Notifications**: Toast messages, email notifications
- **Analytics**: User tracking, metrics dashboard
- **Settings**: User preferences, application configuration
- **Reporting**: Data visualization, export functionality
- **File Management**: Upload, storage, organization
