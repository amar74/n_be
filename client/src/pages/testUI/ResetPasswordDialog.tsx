import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { EnvelopeSimple } from 'phosphor-react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/useToast';
import type { ResetPasswordRequest } from '@/types/auth';
import { ResetPasswordFormSchema } from '@/types/auth';

export function ResetPasswordDialog() {
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const { resetPassword } = useAuth();
  const { toast, presets } = useToast();

  // Initialize form with Zod validation
  const form = useForm<ResetPasswordRequest>({
    resolver: zodResolver(ResetPasswordFormSchema),
    defaultValues: {
      email: '',
    },
    mode: 'onBlur', // Validate on blur for better UX
  });

  const handleSubmit = form.handleSubmit(async (data: ResetPasswordRequest) => {
    setIsSubmitting(true);

    try {
      const { error } = await resetPassword(data.email);

      if (error) {
        console.info('Password reset error:', error.message);

        // Set form error
        form.setError('email', {
          type: 'manual',
          message: error.message,
        });

        // Show error toast using global service
        toast.error('Reset Failed', {
          description: error.message,
          duration: 4000,
        });
      } else {
        console.info('Password reset email sent successfully');

        // Show success toast using global service
        presets.authSuccess('Reset link sent! Check your email.');

        // Set success state
        setSuccess(true);

        // Reset form
        form.reset();
      }
    } catch (err) {
      const errorMessage = 'An unexpected error occurred. Please try again.';

      form.setError('email', {
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

  // Reset states when dialog opens/closes
  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    if (!open) {
      // Reset all states when closing
      setSuccess(false);
      form.reset();
      form.clearErrors();
    }
  };

  // Success state content
  const renderSuccessContent = () => (
    <DialogContent className="sm:max-w-md bg-white !rounded-3xl items-center justify-center p-8">
      <DialogHeader>
        <DialogTitle className="text-2xl font-bold text-green-600 text-center">
          Check your email
        </DialogTitle>
        <DialogDescription className="text-center text-gray-500">
          We've sent you a password reset link. Please check your email and follow the instructions
          to reset your password.
        </DialogDescription>
      </DialogHeader>

      <div className="space-y-6">
        <div className="flex flex-col space-y-3">
          <Button
            onClick={() => handleOpenChange(false)}
            className="w-full bg-[#0F0901] text-white rounded-lg"
          >
            Close
          </Button>
        </div>
      </div>
    </DialogContent>
  );

  // Main form content
  const renderFormContent = () => (
    <DialogContent className="sm:max-w-md bg-white !rounded-3xl items-center justify-center p-8">
      <DialogHeader>
        <DialogTitle className="text-2xl font-bold text-[#ED8A09] text-center">
          Reset your password
        </DialogTitle>
        <DialogDescription className="text-center text-gray-500">
          Enter your e-mail address and we will send you a link to reset your password
        </DialogDescription>
      </DialogHeader>

      <form onSubmit={handleSubmit} className="space-y-6" autoComplete="off">
        {/* Email Input */}
        <Form {...form}>
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email *</FormLabel>
                <FormControl>
                  <div className="relative">
                    <EnvelopeSimple
                      size={20}
                      weight="regular"
                      className="absolute left-2 top-2.5 text-gray-400"
                    />
                    <Input
                      {...field}
                      type="email"
                      autoComplete="off"
                      autoCorrect="off"
                      autoCapitalize="off"
                      spellCheck="false"
                      placeholder="johndoe46@gmail.com"
                      className="pl-10 mt-2 rounded-xl border
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
        </Form>

        {/* Buttons */}
        <div className="flex flex-col space-y-3">
          <Button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-[#0F0901] text-white rounded-lg disabled:opacity-50"
          >
            {isSubmitting ? 'Sending reset link...' : 'Send reset link'}
          </Button>
          <Button
            type="button"
            variant="outline"
            className="w-full rounded-lg"
            onClick={() => handleOpenChange(false)}
          >
            Back to sign-in
          </Button>
        </div>
      </form>
    </DialogContent>
  );

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      {/* Trigger: "Forgot Password?" link */}
      <DialogTrigger asChild>
        <button className="text-[#ED8A09] hover:underline text-sm font-semibold">
          Forgot Password?
        </button>
      </DialogTrigger>

      {/* Modal Content */}
      {success ? renderSuccessContent() : renderFormContent()}
    </Dialog>
  );
}
