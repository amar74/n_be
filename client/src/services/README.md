# Services Documentation

This directory contains API services and HTTP client configuration for the Megapolis application.

## Available Services

### api/client.ts

Main Axios HTTP client with authentication and error handling.

**Features:**

- Base URL configuration from environment variables
- Automatic JWT token injection from localStorage
- Request/response logging in development mode
- Automatic 401 error handling with token cleanup
- Request and response interceptors

**Configuration:**

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});
```

**Token Management:**

- Automatically adds JWT token from localStorage to Authorization header
- Clears tokens and redirects to login on 401 responses
- Supports token refresh workflows

**Usage:**

```typescript
import { apiClient } from '../services/api/client';

// GET request
const response = await apiClient.get('/api/users');

// POST request
const user = await apiClient.post('/api/users', userData);

// Token automatically included in headers
```

### user.service.ts

User-related API service functions.

**Features:**

- User CRUD operations
- Consistent error handling
- TypeScript interfaces for requests/responses

**Available Functions:**

- User data fetching
- Profile updates
- User management operations

## API Client Features

### Request Interceptor

Automatically handles:

- JWT token injection from localStorage
- Request logging in development
- Content-Type headers

### Response Interceptor

Handles:

- Response logging in development
- 401 error processing with automatic logout
- Token cleanup on authentication failures

### Error Handling Strategy

```typescript
// 401 errors trigger automatic cleanup
if (error.response?.status === 401) {
  localStorage.removeItem('jwtToken');
  localStorage.removeItem('supabaseToken');
  localStorage.removeItem('userInfo');
  window.location.href = '/auth/login';
}
```

## Authentication Flow Integration

### Token Verification Process

1. Supabase token sent to `/auth/verify_supabase_token` with Authorization header
2. Backend returns JWT token
3. JWT token stored in localStorage
4. All subsequent API calls include JWT token automatically

### Backend API Endpoints

The client expects these authentication endpoints:

**POST /auth/verify_supabase_token**

- Headers: `Authorization: Bearer {supabase_token}`
- Returns: `{ access_token: "jwt_token", user: {...}, expires_at: "..." }`

**GET /auth/me**

- Headers: `Authorization: Bearer {jwt_token}`
- Returns: `{ user: { id: number, email: string, ... } }`

## Service Patterns

### Service Structure

```typescript
// services/feature.service.ts
import { apiClient } from './api/client';

export interface FeatureData {
  id: number;
  name: string;
  // ... other properties
}

export const featureService = {
  getAll: async (): Promise<FeatureData[]> => {
    const response = await apiClient.get('/api/features');
    return response.data;
  },

  getById: async (id: number): Promise<FeatureData> => {
    const response = await apiClient.get(`/api/features/${id}`);
    return response.data;
  },

  create: async (data: Partial<FeatureData>): Promise<FeatureData> => {
    const response = await apiClient.post('/api/features', data);
    return response.data;
  },

  update: async (id: number, data: Partial<FeatureData>): Promise<FeatureData> => {
    const response = await apiClient.put(`/api/features/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/features/${id}`);
  },
};
```

### Error Handling in Services

```typescript
export const userService = {
  getProfile: async (): Promise<User> => {
    try {
      const response = await apiClient.get('/auth/me');
      return response.data.user;
    } catch (error) {
      if (error instanceof AxiosError) {
        throw new Error(error.response?.data?.message || 'Failed to fetch profile');
      }
      throw error;
    }
  },
};
```

## Development Features

### Request/Response Logging

In development mode, all API calls are logged:

```
🚀 GET /auth/me undefined
✅ GET /auth/me {user: {...}}
❌ GET /auth/verify_supabase_token Network Error
```

### Environment Configuration

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Best Practices

1. **Service Organization**: Group related API calls in service files
2. **Error Handling**: Include proper error handling and user-friendly messages
3. **TypeScript**: Define interfaces for all request/response data
4. **Consistent Patterns**: Follow the established CRUD patterns
5. **Token Management**: Let the client handle authentication automatically
6. **Timeout Handling**: Include appropriate timeouts for API calls
7. **Retry Logic**: Consider implementing retry logic for network errors

## Adding New Services

### 1. Create Service File

```typescript
// services/newFeature.service.ts
import { apiClient } from './api/client';

export interface NewFeatureData {
  // Define data structure
}

export const newFeatureService = {
  // Implement CRUD operations
};
```

### 2. Integration with Redux

```typescript
// In Redux slice
import { newFeatureService } from '../services/newFeature.service';

export const fetchNewFeatureData = createAsyncThunk('newFeature/fetchData', async () => {
  return await newFeatureService.getAll();
});
```

### 3. Use in Components

```typescript
// In component
import { newFeatureService } from '../services/newFeature.service';

const handleCreate = async data => {
  try {
    await newFeatureService.create(data);
    // Handle success
  } catch (error) {
    // Handle error
  }
};
```
