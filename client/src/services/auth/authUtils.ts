import { apiClient } from '@services/api/client';
import { authApi } from '@services/api/authApi';
import { STORAGE_CONSTANTS } from '@/constants/storageConstants';
import { authManager } from './AuthManager';
import type { CurrentUser } from '@/types/auth';

/**
 * Clear all authentication data from localStorage and API client
 */
export const clearAuthData = () => {
  // Clear localStorage
  localStorage.removeItem(STORAGE_CONSTANTS.AUTH_TOKEN);
  localStorage.removeItem(STORAGE_CONSTANTS.USER_INFO);
  
  // Clear API client headers
  delete apiClient.defaults.headers.common['Authorization'];
  
  // Update global auth state
  authManager.setAuthState(false, null);
  authManager.setAuthInProgress(false);
};

/**
 * Restore auth token from localStorage and set it in API client headers
 * Returns true if token was found and set, false otherwise
 */
export const restoreStoredToken = (): boolean => {
  const storedToken = localStorage.getItem(STORAGE_CONSTANTS.AUTH_TOKEN);
  const storedUserInfo = localStorage.getItem(STORAGE_CONSTANTS.USER_INFO);
  
  if (storedToken && storedUserInfo) {
    try {
      // Just set the token in headers, but don't mark as authenticated yet
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      return true;
    } catch (parseError) {
      clearAuthData();
      return false;
    }
  }
  
  return false;
};

/**
 * Authenticate with backend using Supabase token
 */
export const authenticateWithBackend = async (
  supabaseToken: string,
  isMounted: { current: boolean },
  setError: (error: string | null) => void
): Promise<boolean> => {
  // Prevent multiple simultaneous attempts using singleton
  if (authManager.isAuthInProgress()) {
    return false;
  }

  // Check if already authenticated with valid user data
  const { isAuthenticated: globalAuth, backendUser: globalUser } = authManager.getAuthState();
  if (globalAuth && globalUser) {
    return true;
  }

  if (!isMounted.current) return false;

  authManager.setAuthInProgress(true);

  try {
    // Step 1: Exchange Supabase token for backend auth token
    const authResponse = await authApi.verifySupabaseToken(supabaseToken);
    const authToken = authResponse.token;

    if (!authToken) {
      throw new Error('No auth token received from backend');
    }

    if (!isMounted.current) return false;

    // Step 2: Store token in localStorage AND set in API client headers
    localStorage.setItem(STORAGE_CONSTANTS.AUTH_TOKEN, authToken);
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;

    // Step 3: Get fresh user info from /auth/me endpoint
    const userData = await authApi.getMe();
    if (!userData) {
      throw new Error('No user data received from backend');
    }

    if (!isMounted.current) return false;

    // Step 4: Update state and storage with fresh data
    localStorage.setItem(STORAGE_CONSTANTS.USER_INFO, JSON.stringify(userData));
    
    // Update global auth state
    authManager.setAuthState(true, userData);
    setError(null);

    return true;
  } catch (error: any) {
    if (!isMounted.current) return false;
    
    const errorMessage =
      error.response?.data?.message || error.message || 'Authentication failed';
    setError(errorMessage);

    // Clear backend-specific data on failure
    localStorage.removeItem(STORAGE_CONSTANTS.AUTH_TOKEN);
    localStorage.removeItem(STORAGE_CONSTANTS.USER_INFO);
    delete apiClient.defaults.headers.common['Authorization'];
    
    // Update global auth state
    authManager.setAuthState(false, null);

    return false;
  } finally {
    authManager.setAuthInProgress(false);
  }
};
