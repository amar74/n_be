# Layouts Documentation

This directory contains layout components that define the overall structure and routing behavior of the application.

## Purpose

- Provide consistent page structure across the application
- Handle common layout patterns (header, sidebar, footer, etc.)
- Manage responsive design and grid systems
- Wrap pages with common functionality

## Guidelines

- Keep layouts focused on structure, not content
- Use composition patterns to make layouts flexible
- Support different layout variants for different page types
- Include proper TypeScript interfaces for layout props

## Available Layouts

### AuthLayout.tsx

Layout component for authentication pages (login, signup, forgot password).

**Features:**

- Automatic redirect to main app if user is already authenticated
- Centered authentication form design
- Loading state management
- Clean, minimal styling focused on forms

**Usage:**

```typescript
// Used automatically in router configuration
// Wraps all /auth/* routes
<AuthLayout>
  <Outlet /> // LoginPage, SignupPage, ForgotPasswordPage
</AuthLayout>
```

**Behavior:**

- Checks authentication status on mount
- Redirects authenticated users to "/"
- Shows loading spinner during auth checks
- Provides consistent styling for auth forms

### MainLayout.tsx

Layout component for the main application with full authentication protection.

**Features:**

- Authentication gate - redirects unauthenticated users to login
- Includes main navigation component
- Manages complex loading states (Supabase + Backend auth)
- Handles authentication flow coordination
- Error boundary for auth failures

**Usage:**

```typescript
// Used automatically in router configuration
// Wraps all main app routes
<MainLayout>
  <Navigation />
  <main>
    <Outlet /> // HomePage, AccountsPage, UsersPage
  </main>
</MainLayout>
```

**Authentication Flow:**

1. Check Supabase authentication status
2. Verify backend authentication via Redux state
3. Show loading spinner during verification
4. Redirect to login if either check fails
5. Render main app with navigation if authenticated

**Loading States:**

- Initial load detection with 100ms stabilization delay
- Separate loading indicators for different stages
- Grace period for auth flow completion (1 second)
- Prevents flickering between states

## Layout Architecture

### Route Structure

```
/ (MainLayout)
├── / (HomePage)
├── /accounts (AccountsPage)
└── /users (UsersPage)

/auth (AuthLayout)
├── /auth/login (LoginPage)
├── /auth/signup (SignupPage)
└── /auth/forgot-password (ForgotPasswordPage)
```

### Authentication Strategy

- **AuthLayout**: Prevents authenticated users from seeing auth forms
- **MainLayout**: Ensures only authenticated users access main app
- Bidirectional protection prevents auth loops
- Smooth transitions between authenticated/unauthenticated states

### State Management

Both layouts integrate with:

- `useAuth` hook for Supabase authentication
- Redux auth slice for backend user data
- React Router for navigation and redirects
- Loading state coordination across multiple auth systems

## Best Practices

When working with layouts:

- Keep layout-specific logic in layout components
- Use layouts for cross-cutting concerns (auth, navigation, error handling)
- Maintain consistent loading and error states
- Handle edge cases like token expiration gracefully
- Ensure layouts don't interfere with each other's redirect logic
