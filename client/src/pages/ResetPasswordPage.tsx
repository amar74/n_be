import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { LockKey, Eye, EyeClosed } from 'phosphor-react';
import { supabase } from '@lib/supabase';
import { useToast } from '@/hooks/useToast';
import type { ResetPasswordFormRequest } from '@/types/auth';
import { UpdatePasswordFormSchema } from '@/types/auth';
import { ResetPasswordNewFormSchema } from '@/types/auth';
import reseticon from '@/assets/reseticon.png';

export default function ResetPasswordPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isValidSession, setIsValidSession] = useState(false);
  const [showPassword, setShowPassword] = useState({
    new: false,
    confirm: false,
  });
  const navigate = useNavigate();
  const { toast, presets } = useToast();

  // Initialize form with Zod validation
  const form = useForm<ResetPasswordFormRequest>({
    resolver: zodResolver(ResetPasswordNewFormSchema),
    defaultValues: {
      newPassword: '',
      confirmPassword: '',
    },
    mode: 'onBlur', // Validate on blur for better UX
  });

  useEffect(() => {
    // Check if we have a valid session from the recovery link
    const checkSession = async () => {
      try {
        const {
          data: { session },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          toast.error('Invalid Reset Link', {
            description: 'Invalid or expired reset link. Please request a new password reset.',
            duration: 5000,
          });
          return;
        }

        if (session) {
          setIsValidSession(true);
        } else {
          toast.error('Invalid Reset Link', {
            description: 'Invalid or expired reset link. Please request a new password reset.',
            duration: 5000,
          });
        }
      } catch (err) {
        toast.error('Error', {
          description: 'An error occurred. Please try again.',
          duration: 4000,
        });
      }
    };

    checkSession();
  }, [toast]);

  const handleSubmit = form.handleSubmit(async (data: ResetPasswordFormRequest) => {
    setIsSubmitting(true);

    try {
      const { error } = await supabase.auth.updateUser({
        password: data.newPassword,
      });

      if (error) {

        // Set form error
        form.setError('newPassword', {
          type: 'manual',
          message: error.message,
        });

        // Show error toast
        toast.error('Update Failed', {
          description: error.message,
          duration: 4000,
        });
      } else {

        // Show success toast using global service
        presets.authSuccess('Password updated successfully! Redirecting to login...');

        // Reset form
        form.reset();

        // Sign out to ensure user needs to login with new password
        await supabase.auth.signOut();

        // Redirect to login after 2 seconds
        setTimeout(() => {
          navigate('/auth/login', { replace: true });
        }, 2000);
      }
    } catch (err) {
      const errorMessage = 'Failed to update password. Please try again.';

      form.setError('root', {
        type: 'manual',
        message: errorMessage,
      });

      toast.error('Error', {
        description: errorMessage,
        duration: 4000,
      });
    } finally {
      setIsSubmitting(false);
    }
  });

  const handleBackToLogin = () => {
    navigate('/auth/login');
  };

  if (!isValidSession) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 h-screen overflow-hidden">
        {/* Left Side - Loading/Error */}
        <div className="flex items-center justify-center bg-white p-8">
          <Card className="w-full max-w-md shadow-none border-0">
            <CardHeader>
              <CardTitle className="text-3xl font-bold text-orange-500 text-center">
                Verifying Reset Link
              </CardTitle>
              <p className="text-gray-500 text-sm text-center">
                Please wait while we verify your password reset link...
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
              </div>
              <Button
                onClick={handleBackToLogin}
                variant="outline"
                className="w-full rounded-xl py-5 text-center"
              >
                Back to sign-in
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Side - Illustration */}
        <div className="hidden lg:flex mr-22 items-start justify-center p-0 pt-0 h-full relative">
          <div className="w-full h-screen flex items-end justify-end">
            <img
              src={reseticon}
              alt="Password reset illustration"
              className="w-auto max-h-[80%] object-contain absolute bottom-0 right-0"
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 h-screen overflow-hidden">
      {/* CSS to hide default browser password toggle icon */}
      <style>
        {`
          input[type="password"]::-ms-reveal,
          input[type="password"]::-ms-clear,
          input[type="password"]::-webkit-password-visibility-toggle {
            display: none;
          }
        `}
      </style>

      {/* Left Side - Form */}
      <div className="flex items-start justify-center md:ml-6 bg-white p-8 sm:py-34 h-full">
        <Card className="w-full max-w-md shadow-none border-0">
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-orange-500">
              Set New Password
            </CardTitle>
            <p className="text-gray-500 text-sm">
              Please enter your new password and confirm it to update your account.
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <Form {...form}>
              <form onSubmit={handleSubmit} className="space-y-5">
                {/* New Password */}
                <FormField
                  control={form.control}
                  name="newPassword"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>New Password *</FormLabel>
                      <FormControl>
                        <div className="relative mt-2">
                          <LockKey
                            className="absolute left-2.5 top-2.5 h-5 w-5 text-gray-500"
                            weight="duotone"
                          />
                          <Input
                            {...field}
                            type={showPassword.new ? 'text' : 'password'}
                            placeholder="***********"
                            className="pl-10 pr-10 py-5 rounded-xl bg-[#F3F3F3] 
                              placeholder-shown:border-gray-300 
                              focus:border-orange-500 
                              not-placeholder-shown:border-orange-500 
                              focus:outline-none focus:ring-0 focus-visible:ring-0"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            aria-label={showPassword.new ? 'Hide password' : 'Show password'}
                            className="absolute right-2 top-1 h-8 px-2"
                            onClick={() =>
                              setShowPassword({ ...showPassword, new: !showPassword.new })
                            }
                          >
                            {showPassword.new ? (
                              <Eye size={22} weight="duotone" />
                            ) : (
                              <EyeClosed size={22} weight="duotone" />
                            )}
                          </Button>
                        </div>
                      </FormControl>
                      <FormMessage />
                      <p className="text-sm font-medium text-gray-500">
                        Password must be{' '}
                        <span className="text-orange-500">6 characters long.</span>
                      </p>
                    </FormItem>
                  )}
                />

                {/* Confirm Password */}
                <FormField
                  control={form.control}
                  name="confirmPassword"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirm Password *</FormLabel>
                      <FormControl>
                        <div className="relative mt-2">
                          <LockKey
                            className="absolute left-2.5 top-2.5 h-5 w-5 text-gray-400"
                            weight="duotone"
                          />
                          <Input
                            {...field}
                            type={showPassword.confirm ? 'text' : 'password'}
                            placeholder="***********"
                            className="pl-10 pr-10 py-5 rounded-xl bg-[#F3F3F3] 
                              placeholder-shown:border-gray-300 
                              focus:border-orange-500 
                              not-placeholder-shown:border-orange-500 
                              focus:outline-none focus:ring-0 focus-visible:ring-0"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            aria-label={showPassword.confirm ? 'Hide password' : 'Show password'}
                            className="absolute right-2 top-1 h-8 px-2"
                            onClick={() =>
                              setShowPassword({
                                ...showPassword,
                                confirm: !showPassword.confirm,
                              })
                            }
                          >
                            {showPassword.confirm ? (
                              <Eye size={20} weight="duotone" />
                            ) : (
                              <EyeClosed size={20} weight="duotone" />
                            )}
                          </Button>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Global form errors */}
                {form.formState.errors.root && (
                  <div className="text-red-600 text-sm text-center">
                    {form.formState.errors.root.message}
                  </div>
                )}

                {/* Action Buttons */}
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full bg-black text-white py-5 rounded-xl text-center disabled:opacity-50"
                >
                  {isSubmitting ? 'Updating Password...' : 'Update Password'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="w-full rounded-xl py-5 text-center"
                  onClick={handleBackToLogin}
                >
                  Back to sign-in
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>

      {/* Right Side - Illustration */}
      <div className="hidden lg:flex mr-22 items-start justify-center p-0 pt-0 h-full relative">
        <div className="w-full h-screen flex items-end justify-end">
          <img
            src={reseticon}
            alt="Password reset illustration"
            className="w-auto max-h-[80%] object-contain absolute bottom-0 right-0"
          />
        </div>
      </div>
    </div>
  );
}
