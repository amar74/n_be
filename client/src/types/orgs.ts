import { z } from 'zod';
import { schemas } from './generated/orgs';

// Custom schema for Organization to fix datetime validation issue
const OrganizationCustomSchema = z
  .object({
    id: z.string().uuid(),
    owner_id: z.string().uuid(),
    name: z.string(),
    address: z
      .union([
        z.object({
          id: z.string().uuid(),
          line1: z.string(),
          line2: z.union([z.string(), z.null()]).optional(),
          pincode: z.union([z.number(), z.null()]).optional(),
        }),
        z.null(),
      ])
      .optional(),
    website: z.union([z.string(), z.null()]).optional(),
    contact: z
      .union([
        z.object({
          id: z.string().uuid(),
          email: z.union([z.string(), z.null()]).optional(),
          phone: z.union([z.string(), z.null()]).optional(),
        }),
        z.null(),
      ])
      .optional(),
    created_at: z.string(), // Flexible datetime handling for backend format
  })
  .passthrough();

// Export the custom schema for use in API validation
export { OrganizationCustomSchema };

// Re-export generated types (except Organization which we override)
export type OrgCreate = z.infer<typeof schemas.OrgCreateResponse>;
export type OrgCreated = z.infer<typeof schemas.OrgCreatedResponse>;
export type OrgUpdate = z.infer<typeof schemas.OrgUpdateResponse>;
export type CreateOrgRequest = z.infer<typeof schemas.OrgCreateRequest>;
export type Organization = z.infer<typeof OrganizationCustomSchema>; // Use custom schema
export type UpdateOrgRequest = z.infer<typeof schemas.OrgUpdateRequest>;

// Organization members types
export type OrgMemberResponse = z.infer<typeof schemas.OrgMemberResponse>;
export type OrgMembersListResponse = z.infer<typeof schemas.OrgMembersListResponse>;

// Invite types from generated schema
export type InviteCreateRequest = z.infer<typeof schemas.InviteCreateRequest>;
export type InviteResponse = z.infer<typeof schemas.InviteResponse>;
export type AcceptInviteResponse = z.infer<typeof schemas.AcceptInviteResponse>;

// Address and Contact types from generated schema
export type AddressCreateRequest = z.infer<typeof schemas.AddressCreateResquest>;
export type ContactCreateRequest = z.infer<typeof schemas.ContactCreateRequest>;
export type AddressCreateResponse = z.infer<typeof schemas.AddressCreateResponse>;
export type ContactCreateResponse = z.infer<typeof schemas.CreateContactResponse>;

// Business logic extensions
export interface OrgState {
  organization: Organization | null;
  isLoading: boolean;
  error: string | null;
}

export interface OrgListState {
  organizations: Organization[];
  isLoading: boolean;
  error: string | null;
  total: number;
  page: number;
}

export interface CreateOrgFormData {
  name: string;
  address?: {
    line1?: string;
    line2?: string;
    city?: string;
    pincode?: number;
  };
  website?: string;
  contact?: {
    email?: string;
    phone?: string;
  };
}

export interface UpdateOrgFormData {
  name?: string;
  address?: {
    line1?: string;
    line2?: string;
    pincode?: number;
  };
  website?: string;
  contact?: {
    email?: string;
    phone?: string;
  };
}

export interface AddUserFormData {
  email: string;
  role: string;
  createAccount?: boolean;
}

// User role types for organizations
export enum OrgUserRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  MEMBER = 'member',
  VIEWER = 'viewer',
}

export interface OrgUserExtended {
  id: number;
  email: string;
  role: OrgUserRole;
  joinedAt: string;
  isActive: boolean;
  permissions?: string[];
}

// Organization context types
export interface OrgContextValue {
  state: OrgState;
  createOrg: (data: CreateOrgFormData) => Promise<void>;
  updateOrg: (orgId: string, data: UpdateOrgFormData) => Promise<void>;
  addUser: (data: AddUserFormData) => Promise<void>;
  loadOrg: (orgId?: string) => Promise<void>;
  loadMyOrg: () => Promise<void>;
}

// API response types for better error handling
export interface OrgResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export type CreateOrgResponse = OrgResponse<{ organization: Organization }>;
export type UpdateOrgResponse = OrgResponse<{ organization: Organization }>;
export type AddUserResponse = OrgResponse<{ message: string }>;
