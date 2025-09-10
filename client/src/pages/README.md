# Pages Documentation

This directory contains page components that represent different routes in the application.

## Available Pages

### Authentication Pages

#### LoginPage.tsx

User login page with email/password authentication.

**Features:**

- Email and password form validation
- Error handling and display
- Loading states during authentication
- Links to signup and forgot password pages
- Automatic redirect on successful login

**Form Fields:**

- Email (required, email validation)
- Password (required)

**Navigation:**

- Link to signup page
- Link to forgot password page

#### SignupPage.tsx

User registration page with email confirmation flow.

**Features:**

- Email and password registration form
- Password confirmation validation
- Email verification success state
- Error handling for registration failures
- Minimum password length requirement (6 characters)

**Form Fields:**

- Email (required, email validation)
- Password (required, min 6 characters)
- Confirm Password (required, must match password)

**Flow:**

1. User fills form and submits
2. Supabase sends confirmation email
3. Success message displayed
4. User verifies email via link
5. Account becomes active

#### ForgotPasswordPage.tsx

Password reset page with email-based recovery.

**Features:**

- Email input for password reset
- Success state after email sent
- Error handling for invalid emails
- Link back to login page

**Flow:**

1. User enters email address
2. Reset link sent to email
3. User clicks link to reset password
4. Redirected to password reset form

### Main Application Pages

#### HomePage.tsx

Main dashboard page (currently placeholder content).

**Current State:**

- Basic Vite + React demo content
- Counter component for testing
- Development logos and links

**Planned Features:**

- User dashboard with key metrics
- Recent activity feed
- Quick action buttons
- Welcome message with user info

#### AccountsPage.tsx

Accounts management page for viewing and managing user accounts.

**Features:**

- Account listing and management
- Integration with accounts Redux slice
- CRUD operations for accounts

#### UsersPage.tsx

User management page for admin functionality.

**Features:**

- User listing and management
- User data display and editing
- Admin controls for user accounts

## Page Architecture

### Authentication Flow Integration

All pages integrate with the authentication system:

- Auth pages use `useAuth` hook for login/signup actions
- Main pages are protected by `MainLayout` authentication guards
- Automatic redirects based on authentication state

### State Management

Pages connect to Redux store for:

- User authentication state
- Application data (accounts, users)
- Loading and error states
- Form state management

### Error Handling

Consistent error handling patterns:

- Form validation errors
- API request failures
- Network connectivity issues
- User-friendly error messages

### Loading States

All pages implement loading indicators:

- Form submission loading
- Data fetching spinners
- Page transition states
- Skeleton loading for better UX

## Page Patterns

### Common Structure

```typescript
export default function PageName() {
  // Hooks and state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Event handlers
  const handleSubmit = async (e: React.FormEvent) => {
    // Form handling logic
  }

  // Render
  return (
    <div className="page-container">
      {/* Page content */}
    </div>
  )
}
```

### Styling Conventions

- Tailwind CSS for all styling
- Consistent spacing and typography
- Responsive design principles
- Accessible form controls
- Loading and error state styles

## Best Practices

When creating new pages:

1. Follow the established naming convention (PageName.tsx)
2. Include proper TypeScript types
3. Implement loading and error states
4. Add form validation where appropriate
5. Use consistent styling patterns
6. Include proper accessibility attributes
7. Test on different screen sizes
