import { useState, useCallback, useEffect } from 'react';

// Global loading state manager
class LoadingManager {
  private loadingStates = new Set<string>();
  private criticalLoadingStates = new Set<string>();
  private listeners = new Set<() => void>();

  // Define which operations should trigger full-screen loading
  private criticalOperations = new Set(['auth-init', 'auth-signin', 'auth-signup', 'auth-signout']);

  addLoading(key: string) {
    this.loadingStates.add(key);
    if (this.criticalOperations.has(key)) {
      this.criticalLoadingStates.add(key);
    }
    this.notifyListeners();
  }

  removeLoading(key: string) {
    this.loadingStates.delete(key);
    this.criticalLoadingStates.delete(key);
    this.notifyListeners();
  }

  isLoading() {
    return this.loadingStates.size > 0;
  }

  isCriticalLoading() {
    return this.criticalLoadingStates.size > 0;
  }

  getLoadingStates() {
    return Array.from(this.loadingStates);
  }

  getCriticalLoadingStates() {
    return Array.from(this.criticalLoadingStates);
  }

  subscribe(listener: () => void) {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener());
  }
}

// Global instance
const loadingManager = new LoadingManager();

export function useGlobalLoading() {
  const [isLoading, setIsLoading] = useState(loadingManager.isLoading());
  const [isCriticalLoading, setIsCriticalLoading] = useState(loadingManager.isCriticalLoading());

  const addLoading = useCallback((key: string) => {
    loadingManager.addLoading(key);
  }, []);

  const removeLoading = useCallback((key: string) => {
    loadingManager.removeLoading(key);
  }, []);

  const withLoading = useCallback(
    async <T>(key: string, asyncFn: () => Promise<T>): Promise<T> => {
      try {
        addLoading(key);
        return await asyncFn();
      } finally {
        removeLoading(key);
      }
    },
    [addLoading, removeLoading]
  );

  // Subscribe to loading manager updates
  useEffect(() => {
    const unsubscribe = loadingManager.subscribe(() => {
      setIsLoading(loadingManager.isLoading());
      setIsCriticalLoading(loadingManager.isCriticalLoading());
    });
    return unsubscribe;
  }, []);

  return {
    isLoading,
    isCriticalLoading, // New: only true for critical operations
    addLoading,
    removeLoading,
    withLoading,
    getLoadingStates: () => loadingManager.getLoadingStates(),
    getCriticalLoadingStates: () => loadingManager.getCriticalLoadingStates(),
  };
}
