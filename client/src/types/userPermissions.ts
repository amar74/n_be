import { z } from 'zod';
import { schemas } from './generated/user_permissions';
import { AuthUserResponse } from './generated/common';

// Re-export generated types using Zod inference
export type UserPermissionResponse = z.infer<typeof schemas.UserPermissionResponse>;
export type UserPermissionCreateRequest = z.infer<typeof schemas.UserPermissionCreateRequest>;
export type UserPermissionUpdateRequest = z.infer<typeof schemas.UserPermissionUpdateRequest>;
export type UserWithPermissionsResponse = z.infer<typeof schemas.UserWithPermissionsResponse>;

// User type from common schemas
export type User = z.infer<typeof AuthUserResponse>;

// Permissions structure (inferred from UserPermissionResponse)
export type Permissions = Pick<UserPermissionResponse, 'accounts' | 'opportunities' | 'proposals'>;

// Type for the list endpoint response
export type ListUserPermissionsResponse = UserWithPermissionsResponse[];

// Permission categories
export type PermissionCategory = 'accounts' | 'opportunities' | 'proposals';

// Common permission actions
export type PermissionAction = 'view' | 'edit' | 'create' | 'delete';
