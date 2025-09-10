import apiClient from './client';
import type { CurrentUser, SignupSuccess, SignupError } from '../../types/auth';

export const authApi = {
  /**
   * Handle user signup from external auth provider
   */
  async onSignup(email: string): Promise<SignupSuccess> {
    try {
      const { data } = await apiClient.post<SignupSuccess>('/auth/onsignup', { email });
      return data;
    } catch (error: any) {
      // Handle expected signup error response
      if (error.response?.status === 400 && error.response?.data) {
        const errorData = error.response.data as SignupError;
        throw new Error(errorData.message || 'Signup failed');
      }
      throw error;
    }
  },

  /**
   * Verify Supabase token and generate backend JWT
   */
  async verifySupabaseToken(supabaseToken: string): Promise<{ token: string }> {
    const { data } = await apiClient.get<{ token: string }>('/auth/verify_supabase_token', {
      headers: {
        Authorization: `Bearer ${supabaseToken}`,
      },
    });
    return data;
  },

  /**
   * Get current authenticated user info
   */
  async getCurrentUser(): Promise<CurrentUser> {
    const { data } = await apiClient.get<{ user: CurrentUser }>('/auth/me');
    return data.user;
  },

  /**
   * Get just the user object from current user response
   */
  async getMe(): Promise<CurrentUser> {
    const response = await this.getCurrentUser();
    return response;
  },
};
