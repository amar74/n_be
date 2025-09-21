import { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useInviteAcceptance } from '@/hooks/useInviteAcceptance';
import { LoadingCard } from '@/components/invite/LoadingCard';
import { SignupForm } from '@/components/invite/SignupForm';
import { SuccessMessage } from '@/components/invite/SuccessMessage';
import { ErrorCard } from '@/components/invite/ErrorCard';
import { Toaster } from '@/components/ui/toaster';

export default function AcceptInvitePage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const calledRef = useRef(false);

  const {
    isAcceptingInvite,
    inviteData,
    inviteAccepted,
    inviteError,
    isSigningUp,
    signupComplete,
    signupError,
    acceptInvite,
    signup,
    goToLogin,
  } = useInviteAcceptance();

  // Accept invite on component mount - only once
  useEffect(() => {
    if (token && !calledRef.current) {
      calledRef.current = true;
      acceptInvite(token);
    }
  }, [token, acceptInvite]);

  // Handle signup submission
  const handleSignup = async (password: string) => {
    if (!inviteData?.email) {
      goToLogin();
      return;
    }
    await signup({ email: inviteData.email, password });
  };

  return (
    <>
      {/* Loading state while accepting invite */}
      {isAcceptingInvite && <LoadingCard message="Accepting invitation..." />}

      {/* Error state - check for errors OR invalid invite data */}
      {(inviteError || !inviteData || !inviteData.email || !inviteData.role) && (
        <ErrorCard error={inviteError} onGoToLogin={goToLogin} />
      )}

      {/* Success message after signup */}
      {signupComplete && inviteData && (
        <SuccessMessage 
          email={inviteData.email} 
          onGoToLogin={goToLogin} 
        />
      )}

      {/* Show signup form after invite is accepted */}
      {inviteAccepted && inviteData && !signupComplete && (
        <SignupForm
          inviteData={inviteData}
          isSigningUp={isSigningUp}
          onSubmit={handleSignup}
        />
      )}

      {/* Include Toaster for notifications since this is a standalone page */}
      <Toaster />
    </>
  );
}
