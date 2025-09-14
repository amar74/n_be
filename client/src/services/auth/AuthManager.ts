import type { CurrentUser } from '@/types/auth';

/**
 * Singleton AuthManager to prevent multiple simultaneous authentication processes
 * and share auth state across all useAuth hook instances.
 */
export class AuthManager {
  private static instance: AuthManager;
  private authInProgress = false;
  private initializationPromise: Promise<void> | null = null;
  private isAuthenticated = false;
  private backendUser: CurrentUser | null = null;
  private listeners: Set<() => void> = new Set();

  static getInstance(): AuthManager {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }

  /**
   * Subscribe to auth state changes
   */
  subscribe(listener: () => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Notify all listeners of auth state changes
   */
  private notify() {
    this.listeners.forEach(listener => listener());
  }

  /**
   * Update the global authentication state
   */
  setAuthState(isAuth: boolean, user: CurrentUser | null) {
    this.isAuthenticated = isAuth;
    this.backendUser = user;
    this.notify();
  }

  /**
   * Get the current authentication state
   */
  getAuthState() {
    return {
      isAuthenticated: this.isAuthenticated,
      backendUser: this.backendUser
    };
  }

  /**
   * Set whether authentication is currently in progress
   */
  setAuthInProgress(inProgress: boolean) {
    this.authInProgress = inProgress;
  }

  /**
   * Check if authentication is currently in progress
   */
  isAuthInProgress() {
    return this.authInProgress;
  }

  /**
   * Set the initialization promise to prevent multiple simultaneous initializations
   */
  setInitializationPromise(promise: Promise<void> | null) {
    this.initializationPromise = promise;
  }

  /**
   * Get the current initialization promise
   */
  getInitializationPromise() {
    return this.initializationPromise;
  }
}

export const authManager = AuthManager.getInstance();
