import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback, useEffect } from 'react';
import { createQueryKeys } from '@/lib/query-client';
import { accountsApi } from '@/services/api/accountsApi';
import { useToast } from '@/hooks/useToast';
import { parseBackendErrors } from '@/utils/errorParser';
import { AxiosError } from 'axios';
import type {
  AccountCreate,
  AccountUpdate,
  ContactAddRequest,
  ContactUpdateRequest,
} from '@/types/accounts';
import { HTTPValidationError } from '@/types/validationError';

// Query keys using createQueryKeys utility
export const accountsKeys = createQueryKeys('accounts');

// Additional specific query keys for accounts feature
export const accountsQueryKeys = {
  ...accountsKeys,
  list: (params?: Record<string, any>) => [...accountsKeys.all, 'list', params],
  detail: (id: string) => [...accountsKeys.all, 'detail', id],
  contacts: (id: string) => [...accountsKeys.all, 'contacts', id],
  insights: (id: string) => [...accountsKeys.all, 'insights', id],
};

/**
 * Hook for fetching account contacts
 * Only fetches when explicitly called with an account ID
 */
export function useAccountContacts(accountId: string) {
  const {
    data: accountContacts,
    isLoading: isContactsLoading,
    error: contactsError,
  } = useQuery({
    queryKey: accountsQueryKeys.contacts(accountId),
    queryFn: async () => {
      if (!accountId) throw new Error('Account ID is required');
      return accountsApi.getContacts(accountId);
    },
    enabled: !!accountId,
    staleTime: 1000 * 60 * 3, // 3 minutes
  });

  return {
    accountContacts,
    isContactsLoading,
    contactsError,
  };
}

/**
 * Hook for fetching account insights
 * Only fetches when explicitly called with an account ID
 */
export function useAccountInsights(accountId: string) {
  const {
    data: accountInsights,
    isLoading: isInsightsLoading,
    error: insightsError,
  } = useQuery({
    queryKey: accountsQueryKeys.insights(accountId),
    queryFn: async () => {
      if (!accountId) throw new Error('Account ID is required');
      return accountsApi.getAIInsights(accountId);
    },
    enabled: !!accountId,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });

  return {
    accountInsights,
    isInsightsLoading,
    insightsError,
  };
}

/**
 * Hook for fetching a single account's details
 * Only fetches when explicitly called with an account ID
 */
export function useAccountDetail(accountId: string) {
  const {
    data: accountDetail,
    isLoading: isAccountDetailLoading,
    error: accountDetailError,
  } = useQuery({
    queryKey: accountsQueryKeys.detail(accountId),
    queryFn: () => accountsApi.getAccount(accountId),
    enabled: !!accountId,
    staleTime: 1000 * 60 * 2, // 2 minutes
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    accountDetail,
    isAccountDetailLoading,
    accountDetailError,
  };
}

/**
 * Main hook for accounts list and operations
 * @param options.initialParams - Initial search parameters
 * @param options.eager - If true, fetches data immediately on mount (default: true)
 */
export function useAccounts(options?: {
  initialParams?: {
    search?: string;
    tier?: string;
    page?: number;
    size?: number;
  };
  eager?: boolean;
}) {
  const { initialParams, eager = false } = options || {};
  const queryClient = useQueryClient();
  const { toast } = useToast();
  
  // State for lazy loading
  const [enabled, setEnabled] = useState(eager);
  const [queryParams, setQueryParams] = useState(initialParams);
  
  // Error states
  const [createErrors, setCreateErrors] = useState<Record<string, string>>({});
  const [updateErrors, setUpdateErrors] = useState<Record<string, string>>({});

  // Memoize the fetch function to avoid recreating it on every render
  const fetchAccounts = useCallback((params?: typeof initialParams) => {
    setQueryParams(params);
    setEnabled(true);
  }, []);

  // The accounts list query
  const query = useQuery({
    queryKey: accountsQueryKeys.list(queryParams),
    queryFn: async () => accountsApi.listAccounts(queryParams),
    enabled: enabled,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });

  // Mutations
  // Create account mutation
  const createAccountMutation = useMutation({
    mutationFn: async (data: AccountCreate): Promise<{ status_code: number; account_id: string; message: string }> => {
      return await accountsApi.createAccount(data);
    },
    onSuccess: data => {
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.list() });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.detail(data.account_id) });
      toast.success('Account Created', {
        description: data.message || 'Account created successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Creating Account', {
        description: error.response?.data?.message || 'Failed to create account'
      });
    },
  });

  // Update account mutation
  const updateAccountMutation = useMutation({
    mutationFn: async ({
      accountId,
      data,
    }: {
      accountId: string;
      data: AccountUpdate;
    }): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.updateAccount(accountId, data);
    },
    onSuccess: async (data, variables) => {
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.detail(variables.accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.list() });
      toast.success('Account Updated', {
        description: data.message || 'Account updated successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Updating Account', {
        description: error.response?.data?.message || 'Failed to update account'
      });
    },
  });

  // Delete account mutation
  const deleteAccountMutation = useMutation({
    mutationFn: async (accountId: string): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.deleteAccount(accountId);
    },
    onSuccess: (data, accountId) => {
      queryClient.removeQueries({ queryKey: accountsQueryKeys.detail(accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.list() });
      toast.success('Account Deleted', {
        description: data.message || 'Account deleted successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Deleting Account', {
        description: error.response?.data?.message || 'Failed to delete account'
      });
    },
  });

  // Add contact mutation
  const addContactMutation = useMutation({
    mutationFn: async ({
      accountId,
      contact,
    }: {
      accountId: string;
      contact: ContactAddRequest;
    }): Promise<{ status_code: number; contact_id: string; message: string }> => {
      return await accountsApi.addContact(accountId, contact);
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.contacts(variables.accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.detail(variables.accountId) });
      toast.success('Contact Added', {
        description: data.message || 'Contact added successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Adding Contact', {
        description: error.response?.data?.message || 'Failed to add contact'
      });
    },
  });

  // Update contact mutation
  const updateContactMutation = useMutation({
    mutationFn: async ({
      accountId,
      contactId,
      contact,
    }: {
      accountId: string;
      contactId: string;
      contact: ContactUpdateRequest;
    }): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.updateContact(accountId, contactId, contact);
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.contacts(variables.accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.detail(variables.accountId) });
      toast.success('Contact Updated', {
        description: data.message || 'Contact updated successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Updating Contact', {
        description: error.response?.data?.message || 'Failed to update contact'
      });
    },
  });

  // Delete contact mutation
  const deleteContactMutation = useMutation({
    mutationFn: async ({
      accountId,
      contactId,
    }: {
      accountId: string;
      contactId: string;
    }): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.deleteContact(accountId, contactId);
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.contacts(variables.accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.detail(variables.accountId) });
      toast.success('Contact Deleted', {
        description: data.message || 'Contact deleted successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Deleting Contact', {
        description: error.response?.data?.message || 'Failed to delete contact'
      });
    },
  });

  // Promote contact to primary mutation
  const promoteContactToPrimaryMutation = useMutation({
    mutationFn: async ({
      accountId,
      contactId,
    }: {
      accountId: string;
      contactId: string;
    }): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.promoteContactToPrimary(accountId, contactId);
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.contacts(variables.accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.detail(variables.accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.list() });
      toast.success('Contact Promoted', {
        description: data.message || 'Contact has been promoted to primary successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Promoting Contact', {
        description: error.response?.data?.message || 'Failed to promote contact to primary'
      });
    },
  });

  // Generate account report mutation
  const generateReportMutation = useMutation({
    mutationFn: async (accountId: string): Promise<{ report_url: string; report_id: string }> => {
      return await accountsApi.generateAccountReport(accountId);
    },
    onSuccess: (data) => {
      toast.success('Report Generated', {
        description: `Report generated successfully. URL: ${data.report_url}`
      });
    },
    onError: (error: any) => {
      toast.error('Error Generating Report', {
        description: error.response?.data?.message || 'Failed to generate account report'
      });
    },
  });

  // Enrich account data mutation
  const enrichAccountDataMutation = useMutation({
    mutationFn: async (website: string) => {
      return await accountsApi.enrichAccountData(website);
    },
    onSuccess: () => {
      toast.success('Data Enriched', {
        description: 'Account data enriched successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Error Enriching Data', {
        description: error.response?.data?.message || 'Failed to enrich account data'
      });
    },
  });

  // Handle create errors
  useEffect(() => {
    if (createAccountMutation.error) {
      const error = createAccountMutation.error as AxiosError;
      if (error.response?.data) {
        const errors = parseBackendErrors(error.response.data as HTTPValidationError, [
          'client_name',
          'client_type',
          'market_sector',
          'line1',
          'line2',
          'city',
          'pincode',
          'company_website'
        ]);
        if(errors.line1){
          errors.client_address_line1 = errors.line1;
          delete errors.line1;
        }
        if(errors.line2){
          errors.client_address_line2 = errors.line2;
          delete errors.line2;
        }
        if(errors.city){
          errors.client_address_city = errors.city;
          delete errors.city;
        }
        if(errors.pincode){
          errors.client_address_zip_code = errors.pincode;
          delete errors.pincode;
        }
        setCreateErrors(errors);
      }
    } else {
      setCreateErrors({});
    }
  }, [createAccountMutation.error]);

  // Handle update errors
  useEffect(() => {
    if (updateAccountMutation.error) {
      const error = updateAccountMutation.error as AxiosError;
      if (error.response?.data) {
        const errors = parseBackendErrors(error.response.data as HTTPValidationError, [
          'client_name',
          'client_type',
          'market_sector',
          'line1',
          'line2',
          'city',
          'pincode',
          'company_website'
        ]);

        if(errors.line1){
          errors.client_address_line1 = errors.line1;
          delete errors.line1;
        }
        if(errors.line2){
          errors.client_address_line2 = errors.line2;
          delete errors.line2;
        }
        if(errors.city){
          errors.client_address_city = errors.city;
          delete errors.city;
        }
        if(errors.pincode){
          errors.client_address_zip_code = errors.pincode;
          delete errors.pincode;
        }
        setUpdateErrors(errors);
      }
    } else {
      setUpdateErrors({});
    }
  }, [updateAccountMutation.error]);

  // Clear errors on success
  useEffect(() => {
    if (createAccountMutation.isSuccess) {
      setCreateErrors({});
    }
  }, [createAccountMutation.isSuccess]);

  useEffect(() => {
    if (updateAccountMutation.isSuccess) {
      setUpdateErrors({});
    }
  }, [updateAccountMutation.isSuccess]);

  // Return combined functionality
  return {
    // Query functionality
    fetchAccounts,
    accountsList: query.data,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error: query.error,
    refetch: query.refetch,

    // Account mutation actions
    createAccount: createAccountMutation.mutateAsync,
    updateAccount: updateAccountMutation.mutateAsync,
    deleteAccount: deleteAccountMutation.mutateAsync,

    // Account error states
    createAccountError: createAccountMutation.error,
    updateAccountError: updateAccountMutation.error,
    deleteAccountError: deleteAccountMutation.error,
    createErrors,
    updateErrors,

    // Account success states
    isCreateAccountSuccess: createAccountMutation.isSuccess,
    isUpdateAccountSuccess: updateAccountMutation.isSuccess,
    isDeleteAccountSuccess: deleteAccountMutation.isSuccess,

    // Contact mutation actions
    addContact: addContactMutation.mutateAsync,
    updateContact: updateContactMutation.mutateAsync,
    deleteContact: deleteContactMutation.mutateAsync,
    promoteContactToPrimary: promoteContactToPrimaryMutation.mutateAsync,

    // Account mutation states
    isCreating: createAccountMutation.isPending,
    isUpdating: updateAccountMutation.isPending,
    isDeleting: deleteAccountMutation.isPending,

    // Contact mutation states
    isAddingContact: addContactMutation.isPending,
    isUpdatingContact: updateContactMutation.isPending,
    isDeletingContact: deleteContactMutation.isPending,
    isPromotingContact: promoteContactToPrimaryMutation.isPending,

    // Utility mutation actions
    generateReport: generateReportMutation.mutateAsync,
    enrichAccountData: enrichAccountDataMutation.mutateAsync,

    // Utility mutation states
    isGeneratingReport: generateReportMutation.isPending,
    isEnriching: enrichAccountDataMutation.isPending,
  };
}
