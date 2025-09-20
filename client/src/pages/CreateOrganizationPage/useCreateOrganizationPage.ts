import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useOrganizations } from '@/hooks/useOrganizations';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { scraperApi, ApiError } from '@/services/api/scraperApi';
import { supabase } from '@/lib/supabase';
import { apiClient } from '@/services/api/client';
import { authApi } from '@/services/api/authApi';
import { authManager } from '@/services/auth/AuthManager';
import { CreateOrgFormData } from '@/types/orgs';
import { FORM_DEFAULT_VALUES, WEBSITE_ANALYSIS_DELAY } from './CreateOrganizationPage.constants';
import { CreateOrganizationSchema, CreateOrganizationFormData } from './CreateOrganizationPage.schema';

export function useCreateOrganizationPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user, initialAuthComplete, isAuthenticated } = useAuth();
  const { createOrganization, isCreating: isSubmitting } = useOrganizations();
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  
  // Use refs to prevent unnecessary re-renders and debounce API calls
  const analysisTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentWebsiteRef = useRef<string>('');

  const form = useForm<CreateOrganizationFormData>({
    resolver: zodResolver(CreateOrganizationSchema),
    defaultValues: FORM_DEFAULT_VALUES,
    mode: 'onChange', // Validate on change for better UX
  });

  const {
    handleSubmit,
    setValue,
    watch,
    control,
    formState: { errors },
  } = form;

  const websiteValue = watch('website');

  const analyzeWebsite = useCallback(async (website: string) => {
    if (!website || !website.includes('.')) return;

    // Prevent duplicate analysis of the same website
    if (currentWebsiteRef.current === website) {
      return;
    }

    currentWebsiteRef.current = website;
    setIsAnalyzing(true);

    try {
      const scrapeResult = await scraperApi.scraper([website]);
      const result = scrapeResult.results[0];

      if (result.error) {
        throw new Error(`Scraping failed: ${result.error}`);
      }

      const info = result.info;

      if (info?.address) {
        const { line1, line2, city, state, pincode } = info.address;
        setValue(
          'address',
          {
            line1: line1 || '',
            line2: line2 || '',
            city: city || state || '',
            pincode: pincode ? Number(pincode) : undefined,
          },
          { shouldValidate: true }
        );
      }

      if (info?.name) {
        setValue('name', info.name, { shouldValidate: true });
      }

      setShowAISuggestions(true);
      toast({
        title: '🔍 Website Analysis Complete',
        description: 'We auto-filled fields using real data from the website.',
      });
    } catch (error) {
      console.error('❌ CreateOrganizationPage: Website analysis failed:', error);
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
    } finally {
      setIsAnalyzing(false);
    }
  }, [setValue, toast]);

  const handleWebsiteChange = useCallback((value: string) => {
    setValue('website', value, { shouldValidate: true });

    // Clear any existing timeout
    if (analysisTimeoutRef.current) {
      clearTimeout(analysisTimeoutRef.current);
    }

    // Reset suggestions when website changes
    if (value !== currentWebsiteRef.current) {
      setShowAISuggestions(false);
    }

    if (value.includes('.') && value.length > 5) {
      analysisTimeoutRef.current = setTimeout(() => {
        analyzeWebsite(value);
      }, WEBSITE_ANALYSIS_DELAY);
    }
  }, [setValue, analyzeWebsite]);

  const handleSubmitForm = useCallback(async (data: CreateOrganizationFormData) => {
    // Add protocol to website if missing
    let website = data.website;
    if (website && website.trim() && !website.startsWith('http')) {
      website = `https://${website}`;
    }

    try {
      const organizationData: CreateOrgFormData = {
        name: data.name.trim(),
        address:
          data.address?.line1 || data.address?.line2 || data.address?.city || data.address?.pincode
            ? {
                line1: data.address.line1?.trim() || '',
                line2: data.address.line2?.trim() || undefined,
                city: data.address.city?.trim() || undefined,
                pincode: data.address.pincode || undefined,
              }
            : undefined,
        website: website?.trim() || undefined,
        contact:
          data.contact?.email || data.contact?.phone
            ? {
                email: data.contact.email?.trim() || undefined,
                phone: data.contact.phone?.trim() || undefined,
              }
            : undefined,
      };

      await createOrganization(organizationData);
      
      // Refresh backend user data to get updated org_id
      // This is needed because MainLayout checks backendUser.org_id for routing
      try {
        const updatedUserData = await authApi.getMe();
        authManager.setAuthState(true, updatedUserData);
        localStorage.setItem('userInfo', JSON.stringify(updatedUserData));
        
        // Navigate after state is updated
        navigate('/', { replace: true });
      } catch (error) {
        console.error('❌ Failed to refresh user data after org creation:', error);
        // Fallback to page reload if refresh fails
        window.location.href = '/';
      }
    } catch (error) {
      console.error('❌ CreateOrganizationPage: Organization creation failed:', error);
      // Error handling is done in the centralized hook
    }
  }, [createOrganization]);

  const handleSignOut = useCallback(async () => {
    try {
      await supabase.auth.signOut();
      localStorage.clear();
      delete apiClient.defaults.headers.common['Authorization'];
      navigate('/auth/login', { replace: true });
    } catch (error) {
      console.error('❌ CreateOrganizationPage: Sign out failed:', error);
      // Still navigate to login even if sign out fails
      navigate('/auth/login', { replace: true });
    }
  }, [navigate]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (analysisTimeoutRef.current) {
        clearTimeout(analysisTimeoutRef.current);
      }
    };
  }, []);

  return {
    // Form state
    form,
    control,
    errors,
    websiteValue,
    isSubmitting,
    isAnalyzing,
    showAISuggestions,
    user,

    // Auth state
    isAuthLoading: !initialAuthComplete,
    isAuthenticated,

    // Form handlers
    handleSubmit: handleSubmit(handleSubmitForm),
    handleWebsiteChange,
    handleSignOut,
  };
}
