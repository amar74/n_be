import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Building2, Globe, Sparkles } from 'lucide-react';
import { AddressForm } from './components/AddressForm/AddressForm';
import { ContactForm } from './components/ContactForm/ContactForm';
import { STEPS } from './CreateOrganizationPage.constants';
import { useCreateOrganizationPage } from './useCreateOrganizationPage';
import { memo } from 'react';

function CreateOrganizationPage() {
  const {
    form,
    control,
    errors,
    websiteValue,
    isSubmitting,
    isAnalyzing,
    showAISuggestions,
    user,
    isAuthLoading,
    isAuthenticated,
    handleSubmit,
    handleWebsiteChange,
    handleSignOut,
  } = useCreateOrganizationPage();

  // Show loading during auth initialization to prevent flicker
  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-[#FCFCFC] flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm">Initializing...</p>
        </div>
      </div>
    );
  }

  // Redirect if not authenticated (shouldn't happen, but safety check)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#FCFCFC] flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm">Redirecting...</p>
        </div>
      </div>
    );
  }

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
                {STEPS.ORGANIZATION_SETUP.number}
              </div>
              <span className="text-sm font-medium">{STEPS.ORGANIZATION_SETUP.title}</span>
            </div>
          </div>

          {/* Organization Details Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900 mb-1">Organization Details</h2>
              <p className="text-xs text-[#A7A7A7] pb-2 border-b border-[#A7A7A7]">
                Provide information about your organization. Our AI will help auto-complete fields where possible.
              </p>
            </div>

            <Form {...form}>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Company Website */}
                  <FormField
                    control={control}
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
                            <Globe className="absolute  left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                            <Input
                              {...field}
                              type="url"
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
                        <div className="h-4 mt-0.5">
                          <FormMessage className="text-red-500 text-xs" />
                        </div>
                        {websiteValue &&
                          websiteValue.includes('.') &&
                          isAnalyzing &&
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
                    control={control}
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
                        <div className="h-4 mt-0.5">
                          <FormMessage className="text-red-500 text-xs" />
                        </div>
                      </FormItem>
                    )}
                  />
                </div>

                {/* Address Form */}
                <AddressForm 
                  isSubmitting={isSubmitting}
                  showAISuggestions={showAISuggestions}
                />

                {/* Contact Form */}
                <ContactForm
                  control={control}
                  isSubmitting={isSubmitting}
                  userEmail={user?.email}
                />

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
                    onClick={handleSignOut}
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

export default memo(CreateOrganizationPage);
