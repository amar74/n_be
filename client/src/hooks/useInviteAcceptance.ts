import { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { orgsApi } from '@/services/api/orgsApi';
import { authService, type SignupRequest, type SignupResult } from '@/services/auth.service';
import type { AcceptInviteResponse } from '@/types/orgs';

interface InviteAcceptanceState {
  isAcceptingInvite: boolean;
  inviteData: AcceptInviteResponse | null;
  inviteAccepted: boolean;
  error: string | null;
}

interface SignupState {
  isSigningUp: boolean;
  signupComplete: boolean;
  error: string | null;
}

export function useInviteAcceptance() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const acceptingRef = useRef(false);

  const [inviteState, setInviteState] = useState<InviteAcceptanceState>({
    isAcceptingInvite: false,
    inviteData: null,
    inviteAccepted: false,
    error: null,
  });

  const [signupState, setSignupState] = useState<SignupState>({
    isSigningUp: false,
    signupComplete: false,
    error: null,
  });

  const acceptInvite = useCallback(async (token: string): Promise<void> => {
    if (!token.trim()) {
      setInviteState(prev => ({
        ...prev,
        error: 'No invite token found in the URL.'
      }));
      toast({
        title: 'Invalid Invite',
        description: 'No invite token found in the URL.',
        variant: 'destructive',
      });
      return;
    }

    // Prevent duplicate calls using ref
    if (acceptingRef.current || inviteState.isAcceptingInvite || inviteState.inviteAccepted) {
      return;
    }

    acceptingRef.current = true;
    setInviteState(prev => ({ ...prev, isAcceptingInvite: true, error: null }));

    try {
      const response = await orgsApi.acceptInvite(token);
      
      // Validate response data
      if (!response || !response.email || !response.role || !response.org_id) {
        console.error('Invalid response structure:', response);
        throw new Error('Invalid response from invite acceptance API');
      }

      setInviteState(prev => ({
        ...prev,
        isAcceptingInvite: false,
        inviteData: response,
        inviteAccepted: true,
        error: null, // Clear any previous errors
      }));

      toast({
        title: 'Invite Accepted',
        description: 'Your invitation has been accepted successfully.',
      });

    } catch (error: any) {
      console.error('Accept invite error:', error);
      console.error('Error response:', error?.response);
      console.error('Error response data:', error?.response?.data);
      
      const errorMessage = error?.response?.data?.detail?.error?.details || 
                          error?.response?.data?.message ||
                          error?.message ||
                          'Failed to accept invite.';
      
      console.error('Processed error message:', errorMessage);
      
      setInviteState(prev => ({
        ...prev,
        isAcceptingInvite: false,
        error: errorMessage,
      }));

      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });

      // Don't automatically redirect - let user see the error and decide
    } finally {
      acceptingRef.current = false;
    }
  }, [inviteState.isAcceptingInvite, inviteState.inviteAccepted, toast]);

  const signup = useCallback(async (request: SignupRequest): Promise<void> => {
    if (!inviteState.inviteData) {
      throw new Error('No invite data available for signup');
    }

    setSignupState(prev => ({ ...prev, isSigningUp: true, error: null }));

    try {
      const result: SignupResult = await authService.signup({
        email: inviteState.inviteData.email,
        password: request.password,
      });

      if (!result.success) {
        setSignupState(prev => ({
          ...prev,
          isSigningUp: false,
          error: result.error || 'Signup failed',
        }));

        toast({
          title: 'Signup Error',
          description: result.error || 'Signup failed',
          variant: 'destructive',
        });
        return;
      }

      setSignupState(prev => ({
        ...prev,
        isSigningUp: false,
        signupComplete: true,
      }));

      if (result.requiresConfirmation) {
        toast({
          title: 'Account Created',
          description: 'Please check your email and click the confirmation link to activate your account.',
        });
      } else {
        toast({
          title: 'Account Created',
          description: 'Your account has been created successfully.',
        });
        navigate('/auth/login');
      }
    } catch (error) {
      setSignupState(prev => ({
        ...prev,
        isSigningUp: false,
        error: 'An unexpected error occurred during signup.',
      }));

      toast({
        title: 'Error',
        description: 'An unexpected error occurred during signup.',
        variant: 'destructive',
      });
    }
  }, [inviteState.inviteData, toast, navigate]);

  const goToLogin = useCallback(() => {
    navigate('/auth/login');
  }, [navigate]);

  return {
    // Invite state
    isAcceptingInvite: inviteState.isAcceptingInvite,
    inviteData: inviteState.inviteData,
    inviteAccepted: inviteState.inviteAccepted,
    inviteError: inviteState.error,

    // Signup state
    isSigningUp: signupState.isSigningUp,
    signupComplete: signupState.signupComplete,
    signupError: signupState.error,

    // Actions
    acceptInvite,
    signup,
    goToLogin,
  };
}
