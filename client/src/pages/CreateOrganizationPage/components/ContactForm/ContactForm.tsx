import { FormField, FormItem, FormControl, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Mail, Phone } from 'lucide-react';
import type { ContactFormProps } from '../../CreateOrganizationPage.types';

export function ContactForm({ control, isSubmitting, userEmail }: ContactFormProps) {
  return (
    <div>
      <h3 className="font-semibold mb-2">Contact Information</h3>
      <div className="flex items-center gap-4">
        <FormField
          control={control}
          name="contact.email"
          render={({ field }) => (
            <FormItem className="flex-1">
              <FormControl>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    {...field}
                    placeholder={userEmail || 'Enter email address'}
                    className="pl-10 border 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-300 
                      not-placeholder-shown:border-orange-300 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                    disabled={isSubmitting}
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <span className="text-sm text-gray-500">or</span>
        <FormField
          control={control}
          name="contact.phone"
          render={({ field }) => (
            <FormItem className="flex-1">
              <FormControl>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    {...field}
                    placeholder="Phone Number"
                    className="pl-10 border 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-300 
                      not-placeholder-shown:border-orange-300 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                    disabled={isSubmitting}
                  />
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
