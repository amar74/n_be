import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { createQueryKeys } from '@/lib/query-client';
import { orgsApi } from '@/services/api/orgsApi';
import { useToast } from '@/hooks/useToast';
import { OrganizationCustomSchema } from '@/types/orgs';
import type {
  CreateOrgFormData,
  UpdateOrgFormData,
  Organization,
  OrgCreated,
  OrgUpdate,
  AddUserFormData,
} from '@/types/orgs';

// Query keys following Development.md patterns using centralized query-client
export const organizationsKeys = createQueryKeys('organizations');

// Additional specific query keys for organizations feature
export const organizationsQueryKeys = {
  ...organizationsKeys,
  myOrg: () => [...organizationsKeys.all, 'myOrg'] as const,
  members: () => [...organizationsKeys.all, 'members'] as const,
  users: (orgId: string, params?: { skip?: number; limit?: number }) => 
    [...organizationsKeys.all, 'users', orgId, params] as const,
};

/**
 * Unified Organizations hook following Development.md patterns
 * Encapsulates all CRUD operations and cache management for the Organizations feature
 * Uses manual API client from services/api/orgsApi.ts with shared Axios instance and centralized query-client
 * Note: Custom validation applied to handle backend datetime format inconsistencies
 */
export function useOrganizations() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // READ - Get current user's organization
  const useMyOrganization = () => {
    return useQuery({
      queryKey: organizationsQueryKeys.myOrg(),
      queryFn: async (): Promise<Organization> => {
        
        // Use manual API client with custom validation to handle datetime issues
        const response = await orgsApi.getMyOrg();
        const result = OrganizationCustomSchema.parse(response);
        
        return result;
      },
      staleTime: 1000 * 60 * 5, // 5 minutes for org data
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    });
  };

  // READ - Get organization by ID (placeholder - needs backend implementation)
  const useOrganization = (orgId: string | undefined) => {
    return useQuery({
      queryKey: organizationsKeys.detail(orgId || ''),
      queryFn: async (): Promise<Organization> => {
        if (!orgId) throw new Error('Organization ID is required');
        // Note: Backend doesn't have getById endpoint yet, using me() as fallback
        
        // Use manual API client with custom validation to handle datetime issues
        const response = await orgsApi.getMyOrg();
        const result = OrganizationCustomSchema.parse(response);
        
        return result;
      },
      enabled: !!orgId,
      staleTime: 1000 * 60 * 5,
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
  };

  // READ - Get organization members
  // NOTE: Temporarily disabled - manual orgsApi doesn't have getOrgMembers method
  const useOrganizationMembers = () => {
    return useQuery({
      queryKey: organizationsQueryKeys.members(),
      queryFn: async () => {
        // TODO: Add getOrgMembers method to manual orgsApi or use generated API for this endpoint
        return { members: [], total_count: 0 }; // Temporary return empty result
      },
      enabled: false, // Disabled until method is added to manual API
      staleTime: 1000 * 60 * 2, // 2 minutes for member data
      retry: 3,
    });
  };

  // READ - Get organization users with pagination
  // NOTE: Temporarily disabled due to API generation issues with getOrgUsers
  const useOrganizationUsers = (
    orgId: string | undefined,
    params?: { skip?: number; limit?: number }
  ) => {
    return useQuery({
      queryKey: organizationsQueryKeys.users(orgId || '', params),
      queryFn: async () => {
        if (!orgId) throw new Error('Organization ID is required');
        
        // TODO: Fix API call once getOrgUsers generation is resolved
        return [] as any[]; // Temporary return empty array
      },
      enabled: false, // Disabled until API generation is fixed
      staleTime: 1000 * 60 * 2,
      retry: 3,
    });
  };

  // CREATE - Create new organization
  const createOrganizationMutation = useMutation({
    mutationFn: async (formData: CreateOrgFormData): Promise<OrgCreated> => {
      
      // Transform form data to match API schema requirements
      const orgData = {
        name: formData.name,
        address: formData.address ? {
          line1: formData.address.line1 || '',
          line2: formData.address.line2 || null,
          city: formData.address.city || null,
          pincode: formData.address.pincode || null,
        } : null,
        website: formData.website || null,
        contact: formData.contact ? {
          email: formData.contact.email || null,
          phone: formData.contact.phone || null,
        } : null,
      };
      
      const result = await orgsApi.createOrg(orgData as any); // Type assertion needed due to outdated generated schema
      return result;
    },
    onSuccess: (data) => {
      // Invalidate relevant queries using centralized query keys
      queryClient.invalidateQueries({ queryKey: organizationsQueryKeys.myOrg() });
      queryClient.invalidateQueries({ queryKey: organizationsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: organizationsQueryKeys.members() });
      toast.success('Organization Created', {
        description: `Organization "${data.org.name}" has been created successfully`
      });
    },
    onError: (error: any) => {
      toast.error('Organization Creation Failed', {
        description: error?.response?.data?.message || 'Failed to create organization. Please try again.'
      });
    },
  });

  // UPDATE - Update organization
  const updateOrganizationMutation = useMutation({
    mutationFn: async ({ 
      orgId, 
      data 
    }: { 
      orgId: string; 
      data: UpdateOrgFormData 
    }): Promise<OrgUpdate> => {
      
      // Transform form data to match API schema requirements
      const updateData = {
        name: data.name || '',
        address: data.address ? {
          line1: data.address.line1 || '',
          line2: data.address.line2 || null,
          pincode: data.address.pincode || null,
          city: null,
        } : null,
        website: data.website || null,
        contact: data.contact ? {
          email: data.contact.email || null,
          phone: data.contact.phone || null,
        } : null,
      };
      
      const result = await orgsApi.updateOrg(orgId, updateData);
      return result;
    },
    onSuccess: (data, variables) => {
      // Invalidate specific organization and list queries using centralized query keys
      queryClient.invalidateQueries({ queryKey: organizationsKeys.detail(variables.orgId) });
      queryClient.invalidateQueries({ queryKey: organizationsQueryKeys.myOrg() });
      queryClient.invalidateQueries({ queryKey: organizationsKeys.lists() });
      queryClient.invalidateQueries({ queryKey: organizationsQueryKeys.members() });
      toast.success('Organization Updated', {
        description: 'Organization details have been updated successfully'
      });
    },
    onError: (error: any) => {
      toast.error('Update Failed', {
        description: error?.response?.data?.message || 'Failed to update organization. Please try again.'
      });
    },
  });

  // UTILITY - Manual cache invalidation for organizations
  const invalidateOrganizations = () => {
    queryClient.invalidateQueries({ queryKey: organizationsKeys.all });
  };

  // UTILITY - Remove all organization queries (useful for logout)
  const clearOrganizationCache = () => {
    queryClient.removeQueries({ queryKey: organizationsKeys.all });
  };

  // UTILITY - Refetch current user's organization
  const refetchMyOrganization = () => {
    return queryClient.refetchQueries({ queryKey: organizationsQueryKeys.myOrg() });
  };

  // UTILITY - Refetch organization members
  const refetchOrganizationMembers = () => {
    return queryClient.refetchQueries({ queryKey: organizationsQueryKeys.members() });
  };

  return {
    // Query hooks - following useAccounts pattern
    useMyOrganization,
    useOrganization,
    useOrganizationMembers,
    useOrganizationUsers,

    // Mutation functions - async operations
    createOrganization: createOrganizationMutation.mutateAsync,
    updateOrganization: updateOrganizationMutation.mutateAsync,

    // Mutation states - for UI loading states
    isCreating: createOrganizationMutation.isPending,
    isUpdating: updateOrganizationMutation.isPending,
    
    // Error states for granular error handling
    createError: createOrganizationMutation.error,
    updateError: updateOrganizationMutation.error,

    // Utility functions - cache management
    invalidateOrganizations,
    clearOrganizationCache,
    refetchMyOrganization,
    refetchOrganizationMembers,

    // Raw mutation objects for advanced usage
    createOrganizationMutation,
    updateOrganizationMutation,
  };
}

/**
 * Convenience hook for commonly used organization data
 * Follows the pattern from useAccounts for direct data access
 * Returns the current user's organization data with loading/error states
 */
export function useMyOrganization() {
  const { useMyOrganization } = useOrganizations();
  const query = useMyOrganization();
  
  // Log query state for debugging
  
  return query;
}

/**
 * Convenience hook for organization members
 * Returns organization members data with loading/error states
 */
export function useOrganizationMembers() {
  const { useOrganizationMembers } = useOrganizations();
  const query = useOrganizationMembers();
  
  // Log query state for debugging
  
  return query;
}

/**
 * Convenience hook for organization users with pagination
 * Returns organization users data with loading/error states
 */
export function useOrganizationUsers(
  orgId: string | undefined,
  params?: { skip?: number; limit?: number }
) {
  const { useOrganizationUsers } = useOrganizations();
  const query = useOrganizationUsers(orgId, params);
  
  // Log query state for debugging
  
  return query;
}
