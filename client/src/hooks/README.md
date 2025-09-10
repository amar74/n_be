# Hooks Documentation

This directory contains custom React hooks for the Megapolis application.

## Purpose

- Encapsulate complex state logic that can be shared across components
- Provide clean abstractions for common patterns
- Keep components focused on presentation while hooks handle logic

## Guidelines

- Follow the "use" naming convention (e.g., useAuth, useLocalStorage)
- Keep hooks focused on a single responsibility
- Use TypeScript for proper type safety
- Include proper error handling and loading states
- Document hook parameters and return values

## Available Hooks

### useAuth.ts

Primary authentication hook that manages Supabase authentication and backend JWT integration.

**Features:**

- Supabase session management
- Backend token verification and JWT storage
- Redux integration for user data
- Automatic token refresh handling
- Error state management
- Loading state coordination

**Usage:**

```typescript
import { useAuth } from '../hooks/useAuth'

function MyComponent() {
  const {
    user,           // Supabase user
    backendUser,    // Backend user data from /auth/me
    isAuthenticated,
    loading,
    error,
    signIn,
    signUp,
    signOut
  } = useAuth()

  if (loading) return <div>Authenticating...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div>
      <p>Email: {backendUser?.email}</p>
      <p>ID: {backendUser?.id}</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  )
}
```

**Return Values:**

- `user`: Supabase User object
- `session`: Supabase Session object
- `backendUser`: User data from backend API
- `isAuthenticated`: Boolean authentication status
- `loading`: Combined loading state
- `error`: Authentication error message
- `signIn(email, password)`: Login function
- `signUp(email, password)`: Registration function
- `signOut()`: Logout function
- `resetPassword(email)`: Password reset function
- `refreshUserData()`: Manually refresh user data

### redux.ts

Typed Redux hooks for the application.

**Features:**

- Type-safe `useAppDispatch` hook
- Type-safe `useAppSelector` hook
- Proper TypeScript integration with Redux store

**Usage:**

```typescript
import { useAppDispatch, useAppSelector } from '../hooks/redux';

function MyComponent() {
  const dispatch = useAppDispatch();
  const { user, loading } = useAppSelector(state => state.auth);

  // Dispatch actions with full type safety
  const handleAction = () => {
    dispatch(someAction());
  };
}
```

## Types of Hooks

- **Data Fetching**: API calls, caching, synchronization
- **State Management**: Local state abstractions, form handling
- **Side Effects**: Event listeners, timers, subscriptions
- **Utilities**: Common patterns like debouncing, localStorage

## Authentication Flow

The `useAuth` hook implements a complex authentication flow:

1. **Initial Load**: Check for existing Supabase session
2. **Token Verification**: Send Supabase token to backend for verification
3. **JWT Storage**: Store returned JWT token for API calls
4. **User Data Fetch**: Get user information from `/auth/me` endpoint
5. **Redux Integration**: Store user data in Redux state
6. **Session Management**: Handle token refreshes and logout

## Hook Patterns

All hooks follow these patterns:

- **TypeScript**: Full type definitions for parameters and return values
- **Error Handling**: Proper error states and user feedback
- **Loading States**: Consistent loading indicators
- **Cleanup**: Proper cleanup of subscriptions and timers
- **Dependencies**: Minimal and stable dependency arrays

## Example Structure

```
hooks/
├── useAuth.ts
├── useLocalStorage.ts
├── useDebounce.ts
├── useApi.ts
├── redux.ts
└── index.ts
```
