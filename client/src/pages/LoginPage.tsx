import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Checkbox } from '@/components/ui/checkbox';
import { Envelope, Lock, Eye, EyeClosed, House, CaretRight } from 'phosphor-react';
import { ResetPasswordDialog } from './testUI/ResetPasswordDialog';
import { useAuth } from '@/hooks/useAuth';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import type { LoginCredentials, LoginFormData } from '@/types/auth';
import { LoginFormSchema } from '@/types/auth';
import { useToast } from '@/hooks/useToast';
import Frame from '@assets/Frame.png';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const { toast, presets } = useToast();

  // Initialize form with Zod validation
  const form = useForm<LoginFormData>({
    resolver: zodResolver(LoginFormSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
    mode: 'onBlur', // Validate on blur for better UX
  });

  // Test toast on component mount to verify global Sonner is working
  useEffect(() => {
    console.info('LoginPage mounted, testing global toast...');
    const timer = setTimeout(() => {
      toast.info('Login page loaded', {
        description: 'Enter your credentials to sign in.',
        duration: 2000,
      });
    }, 500);

    return () => clearTimeout(timer);
  }, [toast]);

  const onSubmit = form.handleSubmit(async (data: LoginFormData) => {
    setIsSubmitting(true);

    // Clear any previous errors
    form.clearErrors();

    try {
      const credentials: LoginCredentials = {
        email: data.email,
        password: data.password,
      };

      const { error } = await signIn(credentials.email, credentials.password);

      if (error) {
        console.info('Login error:', error.message); // Debug log

        // Check if it's invalid credentials error
        const isInvalidCredentials =
          error.message.toLowerCase().includes('invalid') ||
          error.message.toLowerCase().includes('credentials') ||
          error.message.toLowerCase().includes('password') ||
          error.message.toLowerCase().includes('email');

        if (isInvalidCredentials) {
          // Highlight both email and password fields for invalid credentials
          form.setError('email', {
            type: 'manual',
            message: 'Invalid credentials',
          });
          form.setError('password', {
            type: 'manual',
            message: 'Invalid credentials',
          });

          // Show error toast using global toast service
          console.info('Showing error toast for invalid credentials'); // Debug log
          presets.authError();
        } else {
          // For other errors, just highlight email field
          form.setError('email', {
            type: 'manual',
            message: error.message,
          });

          console.info('Showing error toast for other error'); // Debug log
          toast.error('Sign In Failed', {
            description: error.message,
            duration: 4000,
          });
        }
      } else {
        // Handle "remember me" functionality if needed
        if (data.rememberMe) {
          localStorage.setItem('rememberMe', 'true');
        }

        console.info('Showing success toast using global service'); // Debug log

        // Show success toast using global service - will persist across navigation
        presets.authSuccess('Welcome back!');

        console.log('Success toast created via global service');

        // Add a small delay to allow the toast to show before navigation
        setTimeout(() => {
          console.log('Navigating to home page...');
          navigate('/', { replace: true });
        }, 1500); // 1.5 seconds delay
      }
    } catch (err) {
      const errorMessage = 'An unexpected error occurred. Please try again.';

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

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 h-screen overflow-x-hidden">
      {/* Hide default browser password toggle icon */}
      <style>
        {`
          input[type="password"]::-ms-reveal,
          input[type="password"]::-ms-clear,
          input[type="password"]::-webkit-password-visibility-toggle {
            display: none;
          }
        `}
      </style>

      {/* Left: Sign In Form */}
      <div className="flex sm:ml-10 sm:mb-5 items-center justify-center bg-white">
        <Card className="w-full max-w-md shadow-none border-0">
          <CardHeader className="space-y-2">
            <div className="flex flex-row items-center gap-1">
              <House size={20} className="text-gray-700" />
              <CaretRight size={16} className="text-gray-700" />
              <p className="text-md font-medium text-gray-900">Sign-in</p>
            </div>
            <CardTitle className="text-3xl font-bold text-[#ED8A09]">Sign In</CardTitle>
            <p className="text-gray-400 text-sm font-sans">
              Enter your email and password to sign in
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            <Form {...form}>
              <form onSubmit={onSubmit} className="space-y-5">
                {/* Email Field */}
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email *</FormLabel>
                      <FormControl>
                        <div className="relative mt-2">
                          <Envelope
                            className="absolute left-2 top-2 h-5 w-5 text-gray-400"
                            weight="duotone"
                          />
                          <Input
                            {...field}
                            type="email"
                            placeholder="johndoe46@gmail.com"
                            autoComplete="off"
                            autoCorrect="off"
                            autoCapitalize="off"
                            spellCheck="false"
                            className="pl-10 pr-3 py-2 rounded-xl
                              placeholder-shown:border-gray-300
                              focus:border-[#ED8A09]
                              not-placeholder-shown:border-[#ED8A09]
                              focus:outline-none focus:ring-0 focus-visible:ring-0"
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Password Field */}
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-sm">Password *</FormLabel>
                      <FormControl>
                        <div className="relative mt-2">
                          <Lock className="absolute left-2 top-2 h-5 w-5 text-gray-400" weight="duotone" />
                          <Input
                            {...field}
                            type={showPassword ? 'text' : 'password'}
                            placeholder="********"
                            className="pl-10 pr-10 py-2 rounded-xl
                              placeholder-shown:border-gray-300
                              focus:border-[#ED8A09]
                              not-placeholder-shown:border-[#ED8A09]
                              focus:outline-none focus:ring-0 focus-visible:ring-0"
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-1 top-1 h-8 w-8 p-0 text-gray-500 hover:text-gray-700"
                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                          >
                            {showPassword ? (
                              <EyeClosed size={20} weight="duotone" />
                            ) : (
                              <Eye size={20} weight="duotone" />
                            )}
                          </Button>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Remember Me and Reset Password */}
                <div className="flex items-center justify-between text-sm">
                  <FormField
                    control={form.control}
                    name="rememberMe"
                    render={({ field }) => (
                      <FormItem className="flex items-center space-x-2">
                        <FormControl>
                          <Checkbox
                            checked={field.value}
                            onCheckedChange={field.onChange}
                            className="border-[#ED8A09]"
                          />
                        </FormControl>
                        <FormLabel className="text-[#ED8A09] cursor-pointer">
                          Keep me logged in
                        </FormLabel>
                      </FormItem>
                    )}
                  />
                  <ResetPasswordDialog />
                </div>

                {/* Global form errors */}
                {form.formState.errors.root && (
                  <div className="text-red-600 text-sm text-center">
                    {form.formState.errors.root.message}
                  </div>
                )}

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full bg-black text-white py-2 rounded-xl disabled:opacity-50"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Signing in...' : 'Sign-in'}
                </Button>
              </form>
            </Form>

            {/* Footer */}
            <p className="text-sm text-gray-500">
              Don’t have an account?{' '}
              <a href="/contact" className="text-[#ED8A09] font-medium hover:underline">
                Contact Sales
              </a>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Right: Brand Info */}
      <div className="hidden md:flex flex-row justify-end items-center relative overflow-hidden">
        <img src={Frame} alt="Megapolis Advisory logo" className="max-h-screen object-cover" />
      </div>
    </div>
  );
}
