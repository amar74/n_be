import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback } from 'react';
import { createQueryKeys } from '@/lib/query-client';
import { accountsApi } from '@/services/api/accountsApi';
import { useToast } from './use-toast';
import { accountsQueryKeys } from './useAccounts';
import { ContactAddRequest, ContactUpdateRequest } from '@/types/accounts';

/**
 * Hook for fetching account contacts
 * Only fetches when explicitly called with an account ID
 */
export function useAccountContacts(accountId: string) {
  const queryClient = useQueryClient();

	const {
		data: contactsData,
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

  const { toast } = useToast();

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
      toast({
        title: 'Contact Added',
        description: data.message || 'Contact added successfully',
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
      toast({
        title: 'Contact Promoted',
        description: 'Contact has been promoted to primary successfully',
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


  return {
    contactsData,
    isContactsLoading,
    contactsError,


    // Contact mutation actions
    addContact: addContactMutation.mutateAsync,
    updateContact: updateContactMutation.mutateAsync,
    deleteContact: deleteContactMutation.mutateAsync,
    promoteContactToPrimary: promoteContactToPrimaryMutation.mutateAsync,

   
    // Contact mutation states
    isAddingContact: addContactMutation.isPending,
    isUpdatingContact: updateContactMutation.isPending,
    isDeletingContact: deleteContactMutation.isPending,
    isPromotingContact: promoteContactToPrimaryMutation.isPending,
  };
  }
  