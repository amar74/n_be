import { useEffect, useState, useRef } from 'react';
import type { User, Session } from '@supabase/supabase-js';
import { supabase } from '@lib/supabase';
import { apiClient } from '@services/api/client';
import { authApi } from '@services/api/authApi';
import type { CurrentUser, AuthState } from '@/types/auth';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [backendUser, setBackendUser] = useState<CurrentUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [initialAuthComplete, setInitialAuthComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track backend auth attempts to prevent infinite loops
  const backendAuthAttempted = useRef(false);
  const backendAuthFailed = useRef(false);

  // Create proper AuthState object
  const authState: AuthState = {
    user: backendUser,
    isAuthenticated,
    isLoading: !initialAuthComplete,
    error,
  };

  // Clear all auth data
  const clearAuthData = () => {
    setBackendUser(null);
    setIsAuthenticated(false);
    setError(null);
    delete apiClient.defaults.headers.common['Authorization'];
    // Reset backend auth tracking
    backendAuthAttempted.current = false;
    backendAuthFailed.current = false;
  };

  // Authenticate with backend and get user data (with up to 3 retries)
  const authenticateWithBackend = async (supabaseToken: string) => {
    // Prevent multiple simultaneous attempts
    if (backendAuthAttempted.current && !backendAuthFailed.current) {
      console.info('Backend auth already attempted and successful');
      return true;
    }

    // If we've failed before, allow retry but with some delay
    if (backendAuthFailed.current) {
      console.info('Backend auth failed previously - retrying...');
    }

    backendAuthAttempted.current = true;

    try {
      console.info('Attempting backend authentication...');

      // Step 1: Exchange Supabase token for backend auth token
      const authResponse = await authApi.verifySupabaseToken(supabaseToken);
      const authToken = authResponse.token;

      if (!authToken) {
        throw new Error('No auth token received from backend');
      }

      // Step 2: Set in API client (no local storage)
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;

      // Step 3: Get fresh user info from /auth/me endpoint
      const userData = await authApi.getMe();
      if (!userData) return false;
      // Step 4: Update state and storage with fresh data
      console.log('useAuth: Setting backend user from API', { userData });
      setBackendUser(userData);
      setIsAuthenticated(true);
      setError(null);

      console.info('Backend authentication successful');
      // Reset failure tracking on success
      backendAuthFailed.current = false;
      return true;
    } catch (error: any) {
      console.error('Backend authentication failed:', error);
      const errorMessage =
        error.response?.data?.message || error.message || 'Authentication failed';
      setError(errorMessage);

      // Mark as failed but don't clear everything - preserve Supabase session
      backendAuthFailed.current = true;

      // Only clear backend-specific data
      localStorage.removeItem('authToken');
      localStorage.removeItem('userInfo');
      setBackendUser(null);
      setIsAuthenticated(false);
      delete apiClient.defaults.headers.common['Authorization'];

      console.warn('Will retry backend auth on next attempt');

      return false;
    }

    // Should not reach here, but return false defensively
    return false;
  };

  // Initialize authentication
  useEffect(() => {
    let isMounted = true;

    const initializeAuth = async () => {
      try {
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          console.error('Session error:', error);
          clearAuthData();
          if (isMounted) {
            setInitialAuthComplete(true);
          }
          return;
        }

        if (!isMounted) return;

        setSession(session);
        setUser(session?.user ?? null);

        if (session) {
          const success = await authenticateWithBackend(session.access_token);
          if (!success) {
            // Backend auth failed, but don't clear Supabase session
            // Let the user be redirected to login by the layout component
            console.warn('Backend authentication failed, user needs to re-login');
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        clearAuthData();
      } finally {
        if (isMounted) {
          setInitialAuthComplete(true);
        }
      }
    };

    initializeAuth();

    // Listen for auth state changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (!isMounted) return;

      console.log('Auth state change:', event, !!session);

      setSession(session);
      setUser(session?.user ?? null);

      if (session && (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED')) {
        // Reset backend auth tracking for new sign-ins
        if (event === 'SIGNED_IN') {
          backendAuthAttempted.current = false;
          backendAuthFailed.current = false;
        }
        await authenticateWithBackend(session.access_token);
      } else if (event === 'SIGNED_OUT') {
        clearAuthData();
      }
    });

    return () => {
      isMounted = false;
      subscription.unsubscribe();
    };
  }, []); // Empty dependency array to run only once

  const signIn = async (email: string, password: string) => {
    try {
      setError(null);
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        setError(error.message);
      }

      return { data, error };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign in failed';
      setError(errorMessage);
      return { data: null, error: { message: errorMessage } };
    }
  };

  const signUp = async (email: string, password: string) => {
    try {
      setError(null);
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) {
        setError(error.message);
      }

      return { data, error };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign up failed';
      setError(errorMessage);
      return { data: null, error: { message: errorMessage } };
    }
  };

  const signOut = async () => {
    try {
      setError(null);
      
      // Don't clear auth data immediately - wait for Supabase signOut to complete
      const { error } = await supabase.auth.signOut();

      // Only clear auth data after successful signOut
      clearAuthData();

      if (error) {
        setError(error.message);
      }

      return { error };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign out failed';
      setError(errorMessage);
      return { error: { message: errorMessage } };
    }
  };

  const resetPassword = async (email: string) => {
    try {
      setError(null);
      const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });

      if (error) {
        setError(error.message);
      }

      return { data, error };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Password reset failed';
      setError(errorMessage);
      return { data: null, error: { message: errorMessage } };
    }
  };

  return {
    // Proper AuthState object
    authState,
    // Individual properties for backward compatibility
    user: authState.user,
    // Supabase user data
    supabaseUser: user,
    session,
    // Backend user data (from /auth/me) - for backward compatibility
    backendUser,
    isAuthenticated,
    // Loading states
    initialAuthComplete,
    error,
    // Auth actions
    signIn,
    signUp,
    signOut,
    resetPassword,
  };
}
