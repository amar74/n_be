import { supabase } from '@/lib/supabase';

export interface SignupRequest {
  email: string;
  password: string;
}

export interface SignupResult {
  success: boolean;
  requiresConfirmation: boolean;
  error?: string;
}

export const authService = {
  /**
   * Sign up a new user with Supabase
   */
  async signup({ email, password }: SignupRequest): Promise<SignupResult> {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/login`,
        },
      });

      if (error) {
        return {
          success: false,
          requiresConfirmation: false,
          error: error.message,
        };
      }

      // Check if user needs email confirmation
      const requiresConfirmation = data?.user && !data.session;

      return {
        success: true,
        requiresConfirmation: Boolean(requiresConfirmation),
      };
    } catch (error) {
      return {
        success: false,
        requiresConfirmation: false,
        error: 'An unexpected error occurred during signup.',
      };
    }
  },
};
