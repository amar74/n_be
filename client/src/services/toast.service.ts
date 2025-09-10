/**
 * Global Toast Service
 *
 * Provides a centralized way to show toast notifications across the entire app.
 * This service wraps Sonner and provides type-safe methods for different toast types.
 *
 * The toast system is initialized globally in main.tsx and persists across
 * all route changes, layout switches, and page navigation.
 */

import { toast as sonnerToast, type ExternalToast } from 'sonner';

/**
 * Toast configuration options based on Sonner's ExternalToast
 */
export interface ToastOptions extends Omit<ExternalToast, 'id'> {
  /** Toast ID for programmatic control */
  id?: string | number;
}

/**
 * Toast types for different use cases
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading';

/**
 * Toast service class providing type-safe toast methods
 */
class ToastService {
  /**
   * Show a success toast
   */
  success(message: string, options?: ToastOptions): string | number {
    return sonnerToast.success(message, {
      duration: 4000,
      ...options,
    });
  }

  /**
   * Show an error toast
   */
  error(message: string, options?: ToastOptions): string | number {
    return sonnerToast.error(message, {
      duration: 5000, // Longer duration for errors
      ...options,
    });
  }

  /**
   * Show a warning toast
   */
  warning(message: string, options?: ToastOptions): string | number {
    return sonnerToast.warning(message, {
      duration: 4000,
      ...options,
    });
  }

  /**
   * Show an info toast
   */
  info(message: string, options?: ToastOptions): string | number {
    return sonnerToast.info(message, {
      duration: 3000,
      ...options,
    });
  }

  /**
   * Show a loading toast
   */
  loading(message: string, options?: Omit<ToastOptions, 'duration'>): string | number {
    return sonnerToast.loading(message, options);
  }

  /**
   * Show a generic toast
   */
  message(message: string, options?: ToastOptions): string | number {
    return sonnerToast(message, {
      duration: 3000,
      ...options,
    });
  }

  /**
   * Dismiss a specific toast by ID
   */
  dismiss(toastId?: string | number): void {
    sonnerToast.dismiss(toastId);
  }

  /**
   * Dismiss all toasts
   */
  dismissAll(): void {
    sonnerToast.dismiss();
  }

  /**
   * Create a promise-based toast (useful for async operations)
   */
  promise<T>(
    promise: Promise<T>,
    options: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((error: any) => string);
      duration?: number;
    }
  ): string | number | { unwrap: () => Promise<T> } {
    return sonnerToast.promise(promise, {
      loading: options.loading,
      success: options.success,
      error: options.error,
      duration: options.duration,
    });
  }
}

/**
 * Global toast service instance
 * Use this throughout the app for consistent toast notifications
 */
export const toastService = new ToastService();

/**
 * Predefined toast configurations for common use cases
 */
export const ToastPresets = {
  /**
   * Authentication success toast
   */
  authSuccess: (message: string = '🎉 Welcome back!') =>
    toastService.success(message, {
      //   description: 'You have successfully signed in.',
      duration: 4000,
      style: {
        background: '#10b981',
        color: 'white',
        border: '1px solid #059669',
      },
    }),

  /**
   * Authentication error toast
   */
  authError: (message: string = 'Sign In Failed') =>
    toastService.error(message, {
      description: 'Invalid email or password. Please check your credentials and try again.',
      duration: 5000,
    }),

  /**
   * Network error toast
   */
  networkError: (message: string = 'Network Error') =>
    toastService.error(message, {
      description: 'Please check your internet connection and try again.',
      duration: 5000,
    }),

  /**
   * Save success toast
   */
  saveSuccess: (itemName: string = 'Item') =>
    toastService.success('Saved Successfully', {
      description: `${itemName} has been saved successfully.`,
      duration: 3000,
    }),

  /**
   * Delete success toast
   */
  deleteSuccess: (itemName: string = 'Item') =>
    toastService.success('Deleted Successfully', {
      description: `${itemName} has been deleted successfully.`,
      duration: 3000,
    }),
} as const;
