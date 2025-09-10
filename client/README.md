# Megapolis - React Frontend with Supabase Authentication

A modern React application built with TypeScript, Vite, and Supabase authentication, integrated with a FastAPI backend.

## Features

- 🔐 **Authentication System**: Complete auth flow with Supabase + backend JWT integration
- 🎨 **Modern UI**: Built with React 19, TypeScript, and Tailwind CSS
- 🚀 **Fast Development**: Vite for lightning-fast HMR and builds
- 📱 **Responsive Design**: Mobile-first responsive layouts
- 🛡️ **Protected Routes**: Route-level authentication guards
- 🔄 **State Management**: Redux Toolkit for application state
- 📡 **API Integration**: Axios client with automatic token management
- 🧪 **Type Safety**: Full TypeScript coverage with strict configuration

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite
- **Styling**: Tailwind CSS
- **Authentication**: Supabase Auth + Custom JWT Backend
- **State Management**: Redux Toolkit
- **Routing**: React Router v7
- **HTTP Client**: Axios
- **Development**: ESLint, Prettier, Hot Module Replacement

## Project Structure

```
src/
├── components/          # Reusable UI components
├── hooks/              # Custom React hooks (useAuth, etc.)
├── layouts/            # Layout components (AuthLayout, MainLayout)
├── pages/              # Route-specific page components
├── routes/             # Router configuration
├── services/           # API services and HTTP client
├── store/              # Redux store and slices
├── lib/                # Third-party library configurations
└── types/              # TypeScript type definitions
```

## Authentication Flow

The application implements a dual authentication system:

1. **Supabase Authentication**: Handles user registration, login, and session management
2. **Backend JWT Integration**: Exchanges Supabase tokens for backend JWT tokens
3. **Token Management**: Automatic token refresh and validation

### Authentication Routes

- `/auth/login` - User login
- `/auth/signup` - User registration
- `/auth/forgot-password` - Password reset

### Protected Routes

- `/` - Dashboard (requires authentication)
- `/accounts` - Accounts management
- `/users` - User management

## Getting Started

### Prerequisites

- Node.js 18+ and pnpm
- Supabase project
- **Backend API server running on `http://127.0.0.1:8000`** (required for type generation and API calls)

### Installation

1. **Clone and install dependencies:**

   ```bash
   pnpm install
   ```

2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   ```

   Update `.env` with your Supabase credentials:

   ```env
   VITE_SUPABASE_URL=your_supabase_project_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```

### Development Setup

Follow this sequence every time you start development:

1. **Start the backend API server first:**
   
   Make sure your FastAPI backend is running on `http://127.0.0.1:8000`
   
   Check if API is running:
   ```bash
   curl http://127.0.0.1:8000/openapi.json
   ```

2. **Generate TypeScript types from API:**
   
   ```bash
   pnpm generate:dev
   ```
   
   This pulls the latest API schema and generates types in `src/types/generated/`

3. **Start the frontend development server:**
   
   ```bash
   pnpm dev
   ```

### Backend Integration

The frontend expects the following backend endpoints:

- `GET /auth/verify_supabase_token` - Verify Supabase token and return JWT
  - Headers: `Authorization: Bearer {supabase_token}`
  - Returns: `{ access_token: "jwt_token" }`

- `GET /auth/me` - Get current user information
  - Headers: `Authorization: Bearer {jwt_token}`
  - Returns: User object

## Development

### Available Scripts

- `pnpm generate:dev` - Generate types from local API (run this first)
- `pnpm dev` - Start development server (after type generation)
- `pnpm build` - Build for production
- `pnpm preview` - Preview production build
- `pnpm lint` - Run ESLint
- `pnpm generate:prod` - Generate types from production API

### Code Generation

The project includes API client generation from OpenAPI specs:

```bash
pnpm generate:dev   # uses http://127.0.0.1:8000/openapi.json
pnpm generate:prod  # uses https://api.megapolis.com/openapi.json
```

This generates TypeScript types and API clients from the backend OpenAPI specification.

### Troubleshooting

**Type generation fails:**
- Ensure the backend API server is running on `http://127.0.0.1:8000`
- Check that `/openapi.json` endpoint is accessible: `curl http://127.0.0.1:8000/openapi.json`

**Frontend build errors:**
- Run `pnpm generate:dev` to ensure types are up to date
- Check that all generated types in `src/types/generated/` match the current API

**Authentication errors:**
- Verify Supabase environment variables are correct
- Ensure backend `/auth/verify_supabase_token` endpoint is working

## Authentication Hook Usage

```typescript
import { useAuth } from '../hooks/useAuth'

function MyComponent() {
  const { user, backendUser, loading, signIn, signOut } = useAuth()

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <p>Supabase User: {user?.email}</p>
      <p>Backend User: {backendUser?.name}</p>
      <button onClick={() => signOut()}>Logout</button>
    </div>
  )
}
```

## API Client Usage

```typescript
import { apiClient } from '../services/api/client';

// All requests automatically include JWT token
const response = await apiClient.get('/api/users');
const user = await apiClient.post('/api/users', userData);
```

## Contributing

1. Follow the existing code structure and patterns
2. Use TypeScript for all new code
3. Ensure components are properly typed
4. Add appropriate error handling
5. Test authentication flows thoroughly

## License

This project is private and proprietary.
