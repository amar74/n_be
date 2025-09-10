/**
 * useToast Hook
 *
 * Provides easy access to the global toast service in React components.
 * This hook returns the toast service instance and common toast presets.
 *
 * Example usage:
 * ```tsx
 * import { useToast } from '@/hooks/useToast';
 *
 * function MyComponent() {
 *   const { toast, presets } = useToast();
 *
 *   const handleSuccess = () => {
 *     toast.success('Operation completed!');
 *     // or use preset
 *     presets.authSuccess();
 *   };
 *
 *   return <button onClick={handleSuccess}>Click me</button>;
 * }
 * ```
 */

import {
  toastService,
  ToastPresets,
  type ToastOptions,
  type ToastType,
} from '@/services/toast.service';

/**
 * Hook to access the global toast service
 *
 * @returns Object containing toast service and presets
 */
export function useToast() {
  return {
    /**
     * Main toast service with all methods
     */
    toast: toastService,

    /**
     * Predefined toast configurations for common use cases
     */
    presets: ToastPresets,
  } as const;
}

/**
 * Re-export types for convenience
 */
export type { ToastOptions, ToastType };
