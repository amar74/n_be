import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useOrganizations } from '@/hooks/useOrganizations';
import { CreateOrgFormData } from '@/types/orgs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Building2,
  MapPin,
  Globe,
  Phone,
  Sparkles,
  Mail,
} from 'lucide-react';
import { supabase } from '@/lib/supabase';
import { apiClient } from '@/services/api/client';
import { useToast } from '@/hooks/use-toast';
import { scraperApi, ApiError } from '@/services/api/scraperApi';

export default function CreateOrganizationPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Use centralized hook following Development.md patterns
  const { createOrganization, isCreating } = useOrganizations();
  
  const [contactPhoneOptions, setContactPhoneOptions] = useState<string[]>([]);
  const [contactEmailOptions, setContactEmailOptions] = useState<string[]>([]);
  const [isCustomPhoneSelected, setIsCustomPhoneSelected] = useState(false);
  const [isCustomEmailSelected, setIsCustomEmailSelected] = useState(false);
  const [customPhone, setCustomPhone] = useState('');
  const [customEmail, setCustomEmail] = useState('');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAISuggestions, setShowAISuggestions] = useState(false);

  const form = useForm<CreateOrgFormData>({
    defaultValues: {
      name: '',
      website: '',
      address: {
        line1: '',
        line2: '',
        pincode: undefined,
      },
      contact: {
        email: '',
        phone: '',
      },
    },
  });

  const {
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = form;
  
  // Use centralized loading state for form submission
  const isSubmitting = isCreating;
  
  const websiteValue = watch('website');

  // AI-powered website analysis (simulated)
  const analyzeWebsite = async (website: string) => {
    if (!website || !website.includes('.')) return;

    setIsAnalyzing(true);

    try {
      const scrapeResult = await scraperApi.scraper([website]);

      const result = scrapeResult.results[0];

      if (result.error) {
        throw new Error(`Scraping failed: ${result.error}`);
      }

      const info = result.info;

      console.log('Scraped info:', info);

      if (info?.address) {
        const { line1, line2, city, state, pincode } = info.address;
        setValue(
          'address',
          {
            line1: line1 || [city, state].filter(Boolean).join(', ') || '',
            line2: line2 || '',
            pincode: pincode ? Number(pincode) : undefined,
          },
          { shouldValidate: true }
        );
      }

      if (info?.name) {
        setValue('name', info.name, { shouldValidate: true });
      }
      if (info?.phone?.length! > 0) {
        setContactPhoneOptions(info?.phone!);
      }
      if (info?.email?.length! > 0) {
        setContactEmailOptions(info?.email!);
      }

      setShowAISuggestions(true);

      toast({
        title: '🔍 Website Analysis Complete',
        description: 'We auto-filled fields using real data from the website.',
      });
    } catch (error) {
      if (error instanceof ApiError) {
        toast({
          title: 'Scraper Error',
          description: `API error: ${error.detail?.[0]?.msg || 'Unknown error'}`,
          variant: 'destructive',
        });
      } else {
        toast({
          title: 'Analysis Failed',
          description: (error as Error).message || 'An unknown error occurred.',
          variant: 'destructive',
        });
      }

      console.error('Website analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleWebsiteChange = (value: string) => {
    setValue('website', value, { shouldValidate: true });

    // Trigger AI analysis if website looks valid
    if (value.includes('.') && value.length > 5) {
      console.log('Triggering AI analysis...');
      setTimeout(() => analyzeWebsite(value), 1500);
    }
  };

  const onSubmit = async (data: CreateOrgFormData) => {
    // Basic validation
    if (!data.name?.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Organization name is required.',
        variant: 'destructive',
      });
      return;
    }

    if (data.website && data.website.trim() && !data.website.startsWith('http')) {
      data.website = `https://${data.website}`;
    }

    try {
      // Prepare the data in the required format
      const organizationData: CreateOrgFormData = {
        name: data.name.trim(),
        address:
          data.address?.line1 || data.address?.line2 || data.address?.pincode
            ? {
                line1: data.address.line1?.trim() || '',
                line2: data.address.line2?.trim() || undefined,
                pincode: data.address.pincode || undefined,
              }
            : undefined,
        website: data.website?.trim() || undefined,
        contact:
          data.contact?.email || data.contact?.phone
            ? {
                email: data.contact.email?.trim() || undefined,
                phone: data.contact.phone?.trim() || undefined,
              }
            : undefined,
      };

      console.log('🚀 CreateOrganizationPage: Starting organization creation', {
        orgName: organizationData.name
      });

      await createOrganization(organizationData);

      console.log('✅ CreateOrganizationPage: Organization created successfully');

      // Redirect to home page after successful creation
      navigate('/', { replace: true });
    } catch (error: any) {
      console.error('❌ CreateOrganizationPage: Organization creation failed:', error);
      // Error handling is already done in the centralized hook
    }
  };

  return (
    <div className="min-h-screen bg-[#FCFCFC] font-['Inter',_system-ui,_-apple-system,_sans-serif]">
      <main className="flex-1 flex flex-col items-center px-6 py-4 pt-2">
        {/* Title Section */}
        <div className="text-center mb-3 max-w-xl">
          <h1 className="text-2xl font-bold text-orange-500 mb-2">
            Create Your Organization
          </h1>
          <p className="text-gray-600 text-sm">
            Set up your organization to get started with the platform. You need an organization to access all features and
            collaborate with your team.
          </p>
        </div>

        {/* Form Field */}
        <div className="w-full max-w-3xl p-6 rounded-3xl bg-white shadow-md">
          {/* Progress Indicator */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium bg-orange-500 text-white">
                1
              </div>
              <span className="text-sm font-medium">Organization Setup</span>
            </div>
            <div className="w-8 h-px bg-[#A7A7A7]"></div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium bg-gray-200 text-gray-500">
                2
              </div>
              <span className="text-sm font-medium text-[#A7A7A7]">Platform Access</span>
            </div>
          </div>

          {/* Organization Details Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900 mb-1">Organization Details</h2>
              <p className="text-xs text-[#A7A7A7] pb-2 border-b border-[#A7A7A7]">
                Provide information about your organization. Our AI will help auto-complete field where possible.
              </p>
            </div>

            <Form {...form}>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Company Website */}
                  <FormField
                    control={form.control}
                    name="website"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <div className="flex items-center">
                          <FormLabel className="text-sm font-medium mr-4">
                            Company Website
                          </FormLabel>
                          <Badge
                            variant="secondary"
                            className="bg-[#ED8A09] text-white text-xs px-3 py-0 rounded-2xl flex items-center gap-1"
                          >
                            <Sparkles className="h-3 w-3 text-white" /> AI Enhanced
                          </Badge>
                        </div>
                        <FormControl>
                          <div className="relative">
                            <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input
                              {...field}
                              placeholder="https://your-company.com"
                              className="pl-10 mt-2 border 
                                placeholder-shown:border-gray-300 
                                focus:border-orange-300 
                                not-placeholder-shown:border-orange-300 
                                focus:outline-none focus:ring-0 focus-visible:ring-0"
                              onChange={(e) => handleWebsiteChange(e.target.value)}
                              disabled={isSubmitting}
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                        {websiteValue &&
                          websiteValue.includes('.') &&
                          !isAnalyzing &&
                          !showAISuggestions && (
                            <div className="flex items-center gap-2 text-sm text-purple-600">
                              <Sparkles className="h-4 w-4" />
                              <span>AI will analyze website and auto-populate fields...</span>
                            </div>
                          )}
                      </FormItem>
                    )}
                  />

                  {/* Organization Name */}
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <div className="flex items-center">
                          <FormLabel className="text-sm font-medium">
                            Organization Name *
                          </FormLabel>
                          <span className="ml-4 text-xs invisible">placeholder</span>
                        </div>
                        <FormControl>
                          <div className="relative">
                            <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input
                              {...field}
                              placeholder="Enter Company Name"
                              className={`pl-10 mt-2 border 
                                placeholder-shown:border-gray-300 
                                focus:border-orange-300 
                                not-placeholder-shown:border-orange-300 
                                focus:outline-none focus:ring-0 focus-visible:ring-0 ${
                                  showAISuggestions && field.value ? 'bg-green-50 border-green-200' : ''
                                }`}
                              disabled={isSubmitting}
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* Address */}
                <FormField
                  control={form.control}
                  name="address.line1"
                  render={({ field }) => (
                    <FormItem className="space-y-2">
                      <FormLabel className="text-sm font-medium">
                        Address
                      </FormLabel>
                      <FormControl>
                        <div className="relative">
                          <MapPin className="absolute left-2 top-3 h-4 w-4 text-gray-400" />
                          <textarea
                            {...field}
                            rows={2}
                            placeholder="Enter Company Address"
                            className={`w-full pl-8 pr-2 py-2 border 
                              placeholder-shown:border-gray-300 
                              focus:border-orange-300 
                              not-placeholder-shown:border-orange-300 
                              bg-gray-100 rounded-md resize-none 
                              focus:outline-none focus:ring-0 focus-visible:ring-0 ${
                                showAISuggestions && field.value ? 'bg-green-50 border-green-200' : ''
                              }`}
                            disabled={isSubmitting}
                            onChange={(e) => {
                              field.onChange(e.target.value);
                              setValue('address.line1', e.target.value, { shouldValidate: true });
                            }}
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Contact Information */}
                <div>
                  <h3 className="font-semibold mb-2">Contact Information</h3>
                  <div className="flex items-center gap-4">
                    <FormField
                      control={form.control}
                      name="contact.email"
                      render={({ field }) => (
                        <FormItem className="flex-1">
                          <FormControl>
                            <div className="relative">
                              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                              <Input
                                {...field}
                                placeholder="johndoe46@gmail.com"
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
                      control={form.control}
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

                {/* AI Suggestions Info */}
                {showAISuggestions && (
                  <div className="bg-purple-50 border border-purple-200 rounded-md p-6">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="h-4 w-4 text-purple-600" />
                      <span className="text-sm font-medium text-purple-900">AI Suggestions Applied</span>
                    </div>
                    <p className="text-xs text-purple-700">
                      We've automatically filled in some fields based on your website. Please review and adjust as needed.
                    </p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-6 pt-2 justify-between">
                  <Button 
                    type="button"
                    variant="outline" 
                    className="py-2 text-sm mx-2"
                    onClick={async () => {
                      // Sign out from Supabase
                      await supabase.auth.signOut();
                      // Clear backend auth token
                      localStorage.removeItem('authToken');
                      // Clear API client auth header
                      delete apiClient.defaults.headers.common['Authorization'];
                      // Navigate to login
                      navigate('/auth/login', { replace: true });
                    }}
                    disabled={isSubmitting}
                  >
                    Back to Sign-In
                  </Button>
                  <Button 
                    type="submit"
                    className="py-2 mx-2 text-sm bg-black text-white"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Creating...' : 'Create Organization'}
                  </Button>
                </div>
              </form>
            </Form>
          </div>
        </div>
      </main>
    </div>
  );
}
