# Components Documentation

This directory contains reusable UI components for the Megapolis application.

## Available Components

### Navigation.tsx

Main navigation component with authentication-aware features.

**Features:**

- Active route highlighting
- User information display (email, ID, name)
- Sign out functionality
- Responsive design with Tailwind CSS

**Usage:**

```typescript
import Navigation from '../components/Navigation'

// Used automatically in MainLayout
<Navigation />
```

**Props:**

- None (uses Redux state and routing hooks internally)

**Dependencies:**

- `useAuth` hook for authentication state
- `useAppSelector` for Redux user data
- React Router for navigation and active route detection

## Component Architecture

All components follow these patterns:

- **TypeScript**: Full type safety with proper interfaces
- **Hooks**: Use custom hooks for state management
- **Styling**: Tailwind CSS for consistent design
- **Accessibility**: Proper ARIA labels and semantic HTML
- **Responsive**: Mobile-first approach

## Adding New Components

When creating new components:

1. Use TypeScript with proper type definitions
2. Follow the existing naming conventions
3. Include proper error handling
4. Use the established styling patterns
5. Document props and usage examples
6. Test with different screen sizes
