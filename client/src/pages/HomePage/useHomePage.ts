import { useAuth } from '@/hooks/useAuth';

export function useHomePage() {
  const { user, initialAuthComplete, isAuthenticated } = useAuth();

  return {
    // User state
    user,
    
    // Auth state
    isAuthLoading: !initialAuthComplete,
    isAuthenticated,
  };
}
