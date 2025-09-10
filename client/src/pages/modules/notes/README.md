# Notes Module

This module provides a complete CRUD interface for managing meeting notes within an organization.

## Features

- **List Notes**: View all meeting notes with pagination and search
- **View Note Details**: Read complete note information with metadata
- **Create Notes**: Add new meeting notes with validation
- **Edit Notes**: Update existing notes with form validation
- **Delete Notes**: Remove notes with confirmation dialog

## Pages

### `/module/notes` - Notes List Page
- Displays paginated grid of notes
- Search functionality by title
- Quick actions (view, edit, delete)
- Create new note button

### `/module/notes/create` - Create Note Page
- Form to create new meeting notes
- Real-time validation using Zod
- Date/time picker for meeting schedule
- Rich text area for notes content

### `/module/notes/:noteId` - Note Details Page
- Full note display with formatting
- Metadata information (created by, dates, etc.)
- Action buttons (edit, delete)
- Breadcrumb navigation

### `/module/notes/:noteId/edit` - Edit Note Page
- Pre-populated form with existing note data
- Same validation as create page
- Unsaved changes warning
- Cancel/save functionality

## Architecture

### Types (`src/types/notes.ts`)
- Generated types from OpenAPI schema
- Custom form validation schemas
- Business logic interfaces

### API Layer (`src/services/api/notesApi.ts`)
- Wrapper around axios HTTP client
- Follows same pattern as other API modules
- Automatic JWT token inclusion via interceptors

### Hook (`src/hooks/useNotes.ts`)
- TanStack Query integration
- Unified CRUD operations
- Optimistic updates and cache invalidation
- Error handling with toast notifications

### Components
- Responsive design using Tailwind CSS
- shadcn/ui components for consistency
- Form validation with react-hook-form + Zod
- Loading states and error handling

## Authentication

All API calls automatically include JWT token via axios interceptors configured in `src/services/api/client.ts`.

## Validation

- Client-side validation using Zod schemas
- Server-side validation via OpenAPI generated types
- Form validation with react-hook-form integration

## Navigation

Notes module is accessible via:
- Navigation dropdown → "Meeting Notes"
- Direct URL: `/module/notes`

## Dependencies

- `@tanstack/react-query` - State management and caching
- `react-hook-form` - Form handling
- `@hookform/resolvers` - Zod integration
- `zod` - Schema validation
- `date-fns` - Date formatting
- `lucide-react` - Icons
- `axios` - HTTP client

## Development

The module follows the established patterns from `Development.md`:
- Generated types from OpenAPI schema
- Unified hooks for feature logic
- Consistent error handling
- Responsive UI with Tailwind CSS
- Proper TypeScript coverage
