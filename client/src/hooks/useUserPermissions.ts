import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { createQueryKeys } from '@/lib/query-client';
import { createApiClient } from '@/types/generated/user_permissions';
import { apiClient } from '@/services/api/client';
import { useToast } from './use-toast';
import type {
  UserPermissionCreateRequest,
  UserPermissionUpdateRequest,
  UserPermissionResponse,
  ListUserPermissionsResponse,
} from '@/types/userPermissions';

// Query keys following Development.md patterns
export const userPermissionsKeys = createQueryKeys('userPermissions');

// Initialize the generated API client
const userPermissionsApi = createApiClient(import.meta.env.VITE_API_BASE_URL, { axiosInstance: apiClient });

/**
 * Unified User Permissions hook following Development.md patterns
 * Encapsulates all CRUD operations and cache management for the User Permissions feature
 */
export function useUserPermissions() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // READ - List all users with permissions
  const useUserPermissionsList = (params?: {
    skip?: number;
    limit?: number;
  }) => {
    return useQuery({
      queryKey: userPermissionsKeys.list(params),
      queryFn: async (): Promise<ListUserPermissionsResponse> => {
        return (await userPermissionsApi.listUserPermissions({
          queries: params
        })).data;
      },
      staleTime: 1000 * 60 * 2, // 2 minutes for list data
    });
  };

  // READ - Get specific user permissions
  const useUserPermission = (userid: string | undefined) => {
    return useQuery({
      queryKey: userPermissionsKeys.detail(userid || ''),
      queryFn: async (): Promise<UserPermissionResponse> => {
        if (!userid) throw new Error('User ID is required');
        return await userPermissionsApi.getUserPermission({
          params: { userid }
        });
      },
      enabled: !!userid,
      staleTime: 1000 * 60 * 2, // 2 minutes for detail data
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
    });
  };

  // CREATE - Create user permissions
  const createUserPermissionMutation = useMutation({
    mutationFn: async (data: UserPermissionCreateRequest): Promise<UserPermissionResponse> => {
      return await userPermissionsApi.createUserPermission(data);
    },
    onSuccess: (data) => {
      // Invalidate permissions list to show new permissions
      queryClient.invalidateQueries({ queryKey: userPermissionsKeys.lists() });
      
      // Set the new permissions in cache
      queryClient.setQueryData(userPermissionsKeys.detail(data.userid), data);
      
      toast({
        title: 'Permissions Created',
        description: `Permissions for user created successfully`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Creating Permissions',
        description: error.response?.data?.message || 'Failed to create user permissions',
        variant: 'destructive',
      });
    },
  });

  // UPDATE - Update user permissions
  const updateUserPermissionMutation = useMutation({
    mutationFn: async ({
      userid,
      data,
    }: {
      userid: string;
      data: UserPermissionUpdateRequest;
    }): Promise<UserPermissionResponse> => {
      return await userPermissionsApi.updateUserPermission(data, {
        params: { userid }
      });
    },
    onSuccess: async (data, variables) => {
      // Update the specific user permissions in cache
      queryClient.setQueryData(userPermissionsKeys.detail(variables.userid), data);
      
      // Update list cache if it exists to keep it in sync
      queryClient.setQueryData(userPermissionsKeys.lists(), (oldData: any) => {
        if (!oldData) return oldData;
        
        return oldData.map((userWithPermission: any) => 
          userWithPermission.user.id === variables.userid 
            ? { 
                ...userWithPermission, 
                permissions: {
                  accounts: data.accounts,
                  opportunities: data.opportunities,
                  proposals: data.proposals,
                }
              } 
            : userWithPermission
        );
      });
      
      // Invalidate list queries in background
      queryClient.invalidateQueries({ 
        queryKey: userPermissionsKeys.lists(),
        refetchType: 'none'
      });
      
      toast({
        title: 'Permissions Updated',
        description: `User permissions updated successfully`,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Updating Permissions',
        description: error.response?.data?.message || 'Failed to update user permissions',
        variant: 'destructive',
      });
    },
  });

  // DELETE - Delete user permissions
  const deleteUserPermissionMutation = useMutation({
    mutationFn: async (userid: string): Promise<void> => {
      await userPermissionsApi.deleteUserPermission(undefined, {
        params: { userid }
      });
    },
    onSuccess: (data, userid) => {
      // Remove permissions from cache
      queryClient.removeQueries({ queryKey: userPermissionsKeys.detail(userid) });
      
      // Invalidate list to show permissions removal
      queryClient.invalidateQueries({ queryKey: userPermissionsKeys.lists() });
      
      toast({
        title: 'Permissions Deleted',
        description: 'User permissions deleted successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error Deleting Permissions',
        description: error.response?.data?.message || 'Failed to delete user permissions',
        variant: 'destructive',
      });
    },
  });

  return {
    // Query hooks
    useUserPermissionsList,
    useUserPermission,

    // Mutation actions
    createUserPermission: createUserPermissionMutation.mutateAsync,
    updateUserPermission: updateUserPermissionMutation.mutateAsync,
    deleteUserPermission: deleteUserPermissionMutation.mutateAsync,

    // Mutation state
    isCreating: createUserPermissionMutation.isPending,
    isUpdating: updateUserPermissionMutation.isPending,
    isDeleting: deleteUserPermissionMutation.isPending,

    // Utility functions
    invalidateUserPermissionsList: () => queryClient.invalidateQueries({ queryKey: userPermissionsKeys.lists() }),
    invalidateUserPermission: (userid: string) => 
      queryClient.invalidateQueries({ queryKey: userPermissionsKeys.detail(userid) }),
  };
}
