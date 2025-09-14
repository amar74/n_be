// Export all auth-related services and utilities
export { AuthManager, authManager } from './AuthManager';
export { clearAuthData, restoreStoredToken, authenticateWithBackend } from './authUtils';

// Re-export auth API for convenience
export { authApi } from '@services/api/authApi';
