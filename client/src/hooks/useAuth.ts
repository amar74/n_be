import { useCallback, useEffect, useRef, useState } from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { supabase } from '@lib/supabase';
import type { AuthState, CurrentUser } from '@/types/auth';
import { 
  authManager, 
  authenticateWithBackend, 
  clearAuthData, 
  restoreStoredToken 
} from '@services/auth';

/**
 * Custom hook for managing authentication state and operations.
 * 
 * Provides a unified interface for:
 * - Supabase authentication (sign in/up/out, password reset)
 * - Backend authentication (JWT token management)
 * - Global auth state synchronization across components
 * 
 * @returns Auth state and methods for authentication operations
 */
export function useAuth() {
  // Supabase auth state
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  
  // Backend auth state (managed by AuthManager)
  const [backendUser, setBackendUser] = useState<CurrentUser | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Hook state
  const [initialAuthComplete, setInitialAuthComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Refs for cleanup and race condition prevention
  const isMounted = useRef(true);

  // Subscribe to global auth state changes from AuthManager
  useEffect(() => {
    const updateAuthState = () => {
      if (!isMounted.current) return;
      const { isAuthenticated: globalAuth, backendUser: globalUser } = authManager.getAuthState();
      setIsAuthenticated(globalAuth);
      setBackendUser(globalUser);
    };

    const unsubscribe = authManager.subscribe(updateAuthState);
    
    // Initialize with current state
    updateAuthState();

    return () => {
      unsubscribe();
    };
  }, []);

  // Memoized AuthState object
  const authState: AuthState = {
    user: backendUser,
    isAuthenticated,
    isLoading: !initialAuthComplete,
    error,
  };

  // Auth utility wrappers
  const handleClearAuthData = useCallback(() => {
    if (!isMounted.current) return;
    setError(null);
    clearAuthData();
  }, []);

  const handleAuthenticateWithBackend = useCallback(
    async (supabaseToken: string): Promise<boolean> => {
      return authenticateWithBackend(supabaseToken, isMounted, setError);
    },
    []
  );

  // Initialize authentication
  useEffect(() => {
    isMounted.current = true;

    const initializeAuth = async () => {
      // Prevent multiple simultaneous initialization attempts using singleton
      const existingPromise = authManager.getInitializationPromise();
      if (existingPromise) {
        await existingPromise;
        setInitialAuthComplete(true);
        return;
      }

      // Skip initialization if already complete
      if (initialAuthComplete) {
        return;
      }

      const initPromise = (async () => {
        try {
          // Check for existing stored auth data but don't set auth state yet
          // We'll re-authenticate with backend to ensure everything is fresh
          restoreStoredToken();
          
          const {
            data: { session },
            error,
          } = await supabase.auth.getSession();

          if (error) {
            handleClearAuthData();
            if (isMounted.current) {
              setInitialAuthComplete(true);
            }
            return;
          }

          if (!isMounted.current) return;

          setSession(session);
          setUser(session?.user ?? null);

          if (session) {
            await handleAuthenticateWithBackend(session.access_token);
          } else {
            handleClearAuthData();
          }
        } catch (error) {
          handleClearAuthData();
        } finally {
          if (isMounted.current) {
            setInitialAuthComplete(true);
          }
          authManager.setInitializationPromise(null);
        }
      })();

      authManager.setInitializationPromise(initPromise);
      return initPromise;
    };

    initializeAuth();

    // Listen for Supabase auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (!isMounted.current) return;

        setSession(session);
        setUser(session?.user ?? null);

        switch (event) {
          case 'SIGNED_IN':
            if (session) {
              await handleAuthenticateWithBackend(session.access_token);
            }
            break;
          case 'TOKEN_REFRESHED':
            if (session && !authManager.getAuthState().isAuthenticated) {
              await handleAuthenticateWithBackend(session.access_token);
            }
            break;
          case 'SIGNED_OUT':
            handleClearAuthData();
            break;
        }
      }
    );

    return () => {
      isMounted.current = false;
      subscription.unsubscribe();
    };
  }, []); // Empty dependency array to run only once

  const signIn = useCallback(async (email: string, password: string) => {
    try {
      setError(null);
      const result = await supabase.auth.signInWithPassword({ email, password });
      
      if (result.error) {
        setError(result.error.message);
      }
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign in failed';
      setError(errorMessage);
      return { data: null, error: { message: errorMessage } };
    }
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    try {
      setError(null);
      const result = await supabase.auth.signUp({ email, password });
      
      if (result.error) {
        setError(result.error.message);
      }
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign up failed';
      setError(errorMessage);
      return { data: null, error: { message: errorMessage } };
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      setError(null);
      
      // Clear auth data first to prevent any race conditions
      handleClearAuthData();
      
      // Then sign out from Supabase
      const { error } = await supabase.auth.signOut();

      if (error) {
        setError(error.message);
      }

      return { error };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Sign out failed';
      setError(errorMessage);
      return { error: { message: errorMessage } };
    }
  }, [handleClearAuthData]);

  const resetPassword = useCallback(async (email: string) => {
    try {
      setError(null);
      const result = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`,
      });
      
      if (result.error) {
        setError(result.error.message);
      }
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Password reset failed';
      setError(errorMessage);
      return { data: null, error: { message: errorMessage } };
    }
  }, []);

  return {
    // Primary auth state
    authState,
    user: authState.user,
    isAuthenticated,
    initialAuthComplete,
    error,
    
    // Supabase-specific data
    supabaseUser: user,
    session,
    
    // Backend user data (for backward compatibility)
    backendUser,
    
    // Auth actions
    signIn,
    signUp,
    signOut,
    resetPassword,
  };
}
