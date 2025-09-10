# Routes Documentation

This directory contains routing configuration and components for the Megapolis application.

## Available Files

### AppRouter.tsx

Main router configuration using React Router v7 with nested routes and layouts.

**Route Structure:**

```
/ (MainLayout - Protected)
├── / (HomePage)
├── /accounts (AccountsPage)
└── /users (UsersPage)

/auth (AuthLayout - Public)
├── /auth/login (LoginPage)
├── /auth/signup (SignupPage)
└── /auth/forgot-password (ForgotPasswordPage)
```

**Features:**

- Browser-based routing with `createBrowserRouter`
- Nested route structure with layout components
- Protected routes that require authentication
- Public auth routes for login/signup
- Automatic layout wrapping for route groups

**Usage:**

```typescript
import AppRouter from './routes/AppRouter'

function App() {
  return <AppRouter />
}
```

## Route Protection Strategy

### Protected Routes (MainLayout)

All main application routes require authentication:

- `MainLayout` component acts as a route guard
- Checks both Supabase and backend authentication
- Redirects unauthenticated users to `/auth/login`
- Handles loading states during auth verification

### Public Routes (AuthLayout)

Authentication routes are public but redirect when authenticated:

- `AuthLayout` allows unauthenticated access
- Redirects authenticated users to `/` (main app)
- Prevents authenticated users from seeing login forms

### Route Guards Implementation

```typescript
// In MainLayout.tsx
const { user, isAuthenticated, loading } = useAuth();

useEffect(() => {
  if (!loading && (!user || !isAuthenticated)) {
    navigate('/auth/login', { replace: true });
  }
}, [user, isAuthenticated, loading, navigate]);

// In AuthLayout.tsx
const { user, loading } = useAuth();

useEffect(() => {
  if (!loading && user) {
    navigate('/', { replace: true });
  }
}, [user, loading, navigate]);
```

## Router Configuration

### Browser Router Setup

- Uses `createBrowserRouter` for modern routing
- Supports data loading and error boundaries
- Provides better performance than legacy routers
- Enables future React Router features

### Nested Routes

- Layout components wrap child routes
- `<Outlet />` renders child route components
- Shared layout logic (navigation, auth checks)
- Clean separation of layout and page concerns

### Route Props

- No props passed to route components
- State management through hooks and Redux
- URL parameters via `useParams`
- Query parameters via `useSearchParams`

## Adding New Routes

### Protected Route (Main App)

```typescript
// Add to MainLayout children in AppRouter.tsx
{
  path: '/new-page',
  element: <NewPage />,
}
```

### Public Route (Auth)

```typescript
// Add to AuthLayout children in AppRouter.tsx
{
  path: 'new-auth-page',
  element: <NewAuthPage />,
}
```

### Route with Parameters

```typescript
{
  path: '/users/:id',
  element: <UserDetailPage />,
}

// Access in component
const { id } = useParams()
```

## Best Practices

1. **Route Organization**: Group related routes under appropriate layouts
2. **Path Naming**: Use kebab-case for URLs (`/user-profile`)
3. **Parameters**: Use descriptive parameter names (`:userId` not `:id`)
4. **Redirects**: Use `replace: true` for auth redirects to prevent back button issues
5. **Loading States**: Handle route-level loading in layout components
6. **Error Boundaries**: Add error boundaries for graceful error handling
7. **Code Splitting**: Consider lazy loading for large route components

## Error Handling

The router includes error boundaries and fallbacks:

- Layout-level error boundaries catch route errors
- 404 handling for unknown routes
- Network error recovery
- User-friendly error messages
