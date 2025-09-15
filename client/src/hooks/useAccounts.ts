import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { createQueryKeys } from '@/lib/query-client';
import { accountsApi } from '@/services/api/accountsApi';
import { useToast } from './use-toast';
import type {
  UpdateAccountFormData,
  ContactFormData,
  AccountDetailResponse,
  AccountListResponse,
  AccountListItem,
  AccountCreate,
} from '@/types/accounts';

// Query keys following Development.md patterns
export const accountsKeys = createQueryKeys('accounts');

// Additional specific query keys for accounts feature
export const accountsQueryKeys = {
  ...accountsKeys,
  contacts: (accountId: string) => [...accountsKeys.all, 'contacts', accountId] as const,
  insights: (accountId: string) => [...accountsKeys.all, 'insights', accountId] as const,
  enrichData: (website: string) => [...accountsKeys.all, 'enrich', website] as const,
};

/**
 * Unified Accounts hook following Development.md patterns
 * Encapsulates all CRUD operations and cache management for the Accounts feature
 */
export function useAccounts() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // READ - List accounts with filters - following API.md spec
  const useAccountsList = (params?: {
    search?: string; // Changed from 'q' to 'search' per API.md
    tier?: string;
    page?: number; // Changed from 'offset' to 'page' per API.md
    size?: number; // Changed from 'limit' to 'size' per API.md
  }) => {
    return useQuery({
      queryKey: accountsKeys.list(params),
      queryFn: async (): Promise<AccountListResponse> => {
        return await accountsApi.listAccounts(params);
      },
      staleTime: 1000 * 60 * 2, // 2 minutes for list data
    });
  };

  // READ - Get single account by ID
  const useAccount = (accountId: string | undefined) => {
    const query = useQuery({
      queryKey: accountsKeys.detail(accountId || ''),
      queryFn: async (): Promise<AccountDetailResponse> => {
        console.log('🔍 useAccount: Fetching account data', { accountId });
        if (!accountId) throw new Error('Account ID is required');
        const result = await accountsApi.getAccount(accountId);
        console.log('✅ useAccount: Account data fetched successfully', {
          accountId,
          clientName: result.client_name,
        });
        return result;
      },
      enabled: !!accountId,
      staleTime: 1000 * 60 * 2, // 2 minutes for detail data (reduced for better consistency)
      retry: 3, // Retry failed requests
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    });

    // Log query state changes
    console.log('📊 useAccount query state:', {
      accountId,
      isLoading: query.isLoading,
      isFetching: query.isFetching,
      isError: query.isError,
      hasData: !!query.data,
      error: query.error?.message,
      dataUpdatedAt: new Date(query.dataUpdatedAt).toISOString(),
    });

    return query;
  };

  // READ - Get contacts for an account
  const useAccountContacts = (accountId: string | undefined) => {
    return useQuery({
      queryKey: accountsQueryKeys.contacts(accountId || ''),
      queryFn: async () => {
        if (!accountId) throw new Error('Account ID is required');
        return await accountsApi.getContacts(accountId);
      },
      enabled: !!accountId,
      staleTime: 1000 * 60 * 3, // 3 minutes for contacts
    });
  };

  // READ - Get AI insights for an account
  const useAccountInsights = (accountId: string | undefined) => {
    return useQuery({
      queryKey: accountsQueryKeys.insights(accountId || ''),
      queryFn: async () => {
        if (!accountId) throw new Error('Account ID is required');
        return await accountsApi.getAIInsights(accountId);
      },
      enabled: !!accountId,
      staleTime: 1000 * 60 * 10, // 10 minutes for AI insights
    });
  };

  // CREATE - Create new account - following API.md spec
  const createAccountMutation = useMutation({
    mutationFn: async (
      data: AccountCreate
    ): Promise<{ status_code: number; account_id: string; message: string }> => {
      return await accountsApi.createAccount(data);
    },
    onSuccess: data => {
      // Invalidate accounts list to show new account
      queryClient.invalidateQueries({ queryKey: accountsKeys.list() });

      // Invalidate the specific account to fetch fresh data
      queryClient.invalidateQueries({ queryKey: accountsKeys.detail(data.account_id) });

      toast({
        title: 'Account Created',
        description: data.message || 'Account created successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Creating Account',
        description: error.response?.data?.message || 'Failed to create account',
        variant: 'destructive',
      });
    },
  });

  // UPDATE - Update existing account - following API.md spec
  const updateAccountMutation = useMutation({
    mutationFn: async ({
      accountId,
      data,
    }: {
      accountId: string;
      data: UpdateAccountFormData;
    }): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.updateAccount(accountId, data);
    },
    onSuccess: async (data, variables) => {
      console.log('🔄 updateAccountMutation: Account updated successfully', {
        accountId: variables.accountId,
        message: data.message,
      });

      // Invalidate account detail to fetch fresh data
      queryClient.invalidateQueries({ queryKey: accountsKeys.detail(variables.accountId) });

      // Also invalidate accounts list to reflect any changes
      queryClient.invalidateQueries({ queryKey: accountsKeys.list() });

      toast({
        title: 'Account Updated',
        description: data.message || 'Account updated successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Updating Account',
        description: error.response?.data?.message || 'Failed to update account',
        variant: 'destructive',
      });
    },
  });

  // DELETE - Delete account - following API.md spec
  const deleteAccountMutation = useMutation({
    mutationFn: async (accountId: string): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.deleteAccount(accountId);
    },
    onSuccess: (data, accountId) => {
      // Remove account from cache
      queryClient.removeQueries({ queryKey: accountsKeys.detail(accountId) });

      // Invalidate list to show account removal
      queryClient.invalidateQueries({ queryKey: accountsKeys.list() });

      toast({
        title: 'Account Deleted',
        description: data.message || 'Account deleted successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Deleting Account',
        description: error.response?.data?.message || 'Failed to delete account',
        variant: 'destructive',
      });
    },
  });

  // CREATE - Add secondary contact to account - following API.md spec
  const addContactMutation = useMutation({
    mutationFn: async ({
      accountId,
      contact,
    }: {
      accountId: string;
      contact: ContactFormData;
    }): Promise<{ status_code: number; contact_id: string; message: string }> => {
      return await accountsApi.addContact(accountId, contact);
    },
    onSuccess: (data, variables) => {
      // Invalidate contacts for this account
      queryClient.invalidateQueries({
        queryKey: accountsQueryKeys.contacts(variables.accountId),
      });

      // Also invalidate the account detail to refresh contact count
      queryClient.invalidateQueries({
        queryKey: accountsKeys.detail(variables.accountId),
      });

      toast({
        title: 'Contact Added',
        description: data.message || 'Contact added to account successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Adding Contact',
        description: error.response?.data?.message || 'Failed to add contact',
        variant: 'destructive',
      });
    },
  });

  // UPDATE - Update contact (primary or secondary) - following API.md spec
  const updateContactMutation = useMutation({
    mutationFn: async ({
      accountId,
      contactId,
      contact,
    }: {
      accountId: string;
      contactId: string;
      contact: ContactFormData;
    }): Promise<{ status_code: number; message: string }> => {
      return await accountsApi.updateContact(accountId, contactId, contact);
    },
    onSuccess: (data, variables) => {
      // Invalidate contacts for this account
      queryClient.invalidateQueries({
        queryKey: accountsQueryKeys.contacts(variables.accountId),
      });

      // Also invalidate the account detail to refresh contact data
      queryClient.invalidateQueries({
        queryKey: accountsKeys.detail(variables.accountId),
      });

      toast({
        title: 'Contact Updated',
        description: data.message || 'Contact updated successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Updating Contact',
        description: error.response?.data?.message || 'Failed to update contact',
        variant: 'destructive',
      });
    },
  });

  // DELETE - Delete secondary contact - following API.md spec (primary contacts cannot be deleted)
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
      // Invalidate contacts for this account
      queryClient.invalidateQueries({
        queryKey: accountsQueryKeys.contacts(variables.accountId),
      });

      // Also invalidate the account detail to refresh contact data
      queryClient.invalidateQueries({
        queryKey: accountsKeys.detail(variables.accountId),
      });

      toast({
        title: 'Contact Deleted',
        description: data.message || 'Contact deleted successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Deleting Contact',
        description: error.response?.data?.message || 'Failed to delete contact',
        variant: 'destructive',
      });
    },
  });

  // WRITE - Promote contact to primary
  const promoteContactToPrimaryMutation = useMutation({
    mutationFn: async ({ accountId, contactId }: { accountId: string; contactId: string }) => {
      return await accountsApi.promoteContactToPrimary(accountId, contactId);
    },
    onSuccess: (data, { accountId }) => {
      // Invalidate account details and contacts to refresh the data
      queryClient.invalidateQueries({ queryKey: accountsKeys.detail(accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.contacts(accountId) });
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.all });

      toast({
        title: '✅ Primary Contact Updated',
        description: 'Contact has been promoted to primary successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Promoting Contact',
        description: error.response?.data?.message || 'Failed to promote contact to primary',
        variant: 'destructive',
      });
    },
  });

  // UTILITY - Enrich account data from website
  const enrichAccountDataMutation = useMutation({
    mutationFn: async (website: string) => {
      return await accountsApi.enrichAccountData(website);
    },
    onError: (error: any) => {
      toast({
        title: 'Error Enriching Data',
        description: error.response?.data?.message || 'Failed to enrich account data',
        variant: 'destructive',
      });
    },
  });

  // UTILITY - Generate account report
  const generateReportMutation = useMutation({
    mutationFn: async (accountId: string) => {
      return await accountsApi.generateAccountReport(accountId);
    },
    onError: (error: any) => {
      toast({
        title: 'Error Generating Report',
        description: error.response?.data?.message || 'Failed to generate account report',
        variant: 'destructive',
      });
    },
  });

  return {
    // Query hooks
    useAccountsList,
    useAccount,
    useAccountContacts,
    useAccountInsights,

    // Mutation actions
    createAccount: createAccountMutation.mutateAsync,
    updateAccount: updateAccountMutation.mutateAsync,
    deleteAccount: deleteAccountMutation.mutateAsync,
    addContact: addContactMutation.mutateAsync,
    updateContact: updateContactMutation.mutateAsync,
    deleteContact: deleteContactMutation.mutateAsync,
    promoteContactToPrimary: promoteContactToPrimaryMutation.mutateAsync,
    enrichAccountData: enrichAccountDataMutation.mutateAsync,
    generateReport: generateReportMutation.mutateAsync,

    // Mutation state
    isCreating: createAccountMutation.isPending,
    isUpdating: updateAccountMutation.isPending,
    isDeleting: deleteAccountMutation.isPending,
    isAddingContact: addContactMutation.isPending,
    isUpdatingContact: updateContactMutation.isPending,
    isDeletingContact: deleteContactMutation.isPending,
    isPromotingContact: promoteContactToPrimaryMutation.isPending,
    isEnriching: enrichAccountDataMutation.isPending,
    isGeneratingReport: generateReportMutation.isPending,

    // Utility functions
    invalidateAccountsList: () => queryClient.invalidateQueries({ queryKey: accountsKeys.lists() }),
    invalidateAccount: (accountId: string) =>
      queryClient.invalidateQueries({ queryKey: accountsKeys.detail(accountId) }),
    invalidateAccountContacts: (accountId: string) =>
      queryClient.invalidateQueries({ queryKey: accountsQueryKeys.contacts(accountId) }),
  };
}
