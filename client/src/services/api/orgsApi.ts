import {
  CreateOrgRequest,
  OrgCreated,
  Organization,
  UpdateOrgRequest,
  OrgUpdate,
  OrgMembersListResponse,
  InviteCreateRequest,
  InviteResponse,
  AcceptInviteResponse,
} from '@/types/orgs';
import apiClient from './client';

export const orgsApi = {
  /**
   * Create a new organization
   */
  async createOrg(data: CreateOrgRequest): Promise<OrgCreated> {
    const { data: response } = await apiClient.post<OrgCreated>('/orgs/create', data);
    return response;
  },

  /**
   * Get current user's organization
   */
  async getMyOrg(): Promise<Organization> {
    const { data } = await apiClient.get<Organization>('/orgs/me');
    return data;
  },

  /**
   * Get organization by ID
   */
  async getOrgById(orgId: string): Promise<Organization> {
    const { data } = await apiClient.get<Organization>(`/orgs/${orgId}`);
    return data;
  },

  /**
   * Update organization
   */
  async updateOrg(orgId: string, data: UpdateOrgRequest): Promise<OrgUpdate> {
    const { data: response } = await apiClient.put<OrgUpdate>(`/orgs/update/${orgId}`, data);
    return response;
  },

  /**
   * Get organization members
   */
  async getOrgMembers(): Promise<OrgMembersListResponse> {
    const { data } = await apiClient.get<OrgMembersListResponse>('/orgs/members');
    return data;
  },

  /**
   * Invite a user to the organization
   */
  async inviteMember(inviteData: InviteCreateRequest): Promise<InviteResponse> {
    const { data } = await apiClient.post<InviteResponse>('/orgs/invite', inviteData);
    return data;
  },

  /**
   * Accept an organization invite
   */
  async acceptInvite(token: string): Promise<AcceptInviteResponse> {
    const { data } = await apiClient.post<AcceptInviteResponse>('/orgs/invite/accept', { token });
    return data;
  },

  /**
   * Hello endpoint for testing
   */
  async hello(): Promise<unknown> {
    const { data } = await apiClient.get('/orgs/hello');
    return data;
  },
};
