import { QueryClient } from '@tanstack/react-query';

/**
 * Centralized TanStack Query client configuration
 * Following Development.md strict patterns for query management
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes by default
      staleTime: 1000 * 60 * 5,
      // Keep unused data in cache for 10 minutes
      gcTime: 1000 * 60 * 10,
      // Retry failed requests 3 times with exponential backoff
      retry: 3,
      // Don't refetch on window focus in development to reduce noise
      refetchOnWindowFocus: import.meta.env.PROD,
      // Only refetch on reconnect in production
      refetchOnReconnect: import.meta.env.PROD,
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
      // Show errors for mutations by default
      throwOnError: false,
    },
  },
});

/**
 * Global query key factory for consistent namespacing
 * Ensures all queries follow the ['feature', 'operation'] pattern from Development.md
 */
export const createQueryKeys = <T extends string>(feature: T) => ({
  all: [feature] as const,
  lists: () => [...createQueryKeys(feature).all, 'list'] as const,
  list: (filters?: Record<string, unknown>) => 
    [...createQueryKeys(feature).lists(), filters] as const,
  details: () => [...createQueryKeys(feature).all, 'detail'] as const,
  detail: (id: string | number) => 
    [...createQueryKeys(feature).details(), id] as const,
});

/**
 * Utility function to invalidate all queries for a feature
 * Useful for global state management and cache cleanup
 */
export const invalidateFeature = (feature: string) => {
  return queryClient.invalidateQueries({ 
    queryKey: [feature],
    exact: false 
  });
};

/**
 * Utility function to remove all queries for a feature
 * Useful for logout scenarios or when switching contexts
 */
export const removeFeatureQueries = (feature: string) => {
  return queryClient.removeQueries({ 
    queryKey: [feature],
    exact: false 
  });
};
