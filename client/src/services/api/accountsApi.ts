import { apiClient } from './client';
import { scraperApi } from './scraperApi';
import {
  AccountCreate,
  AccountUpdate,
  AccountDetailResponse,
  AccountListResponse,
  ContactResponse,
  ContactFormData,
  ContactAddRequest,
  ContactUpdateRequest,
  ContactListResponse,
} from '@/types/accounts';

class AccountsApiService {
  private baseURL = '/accounts';

  // List accounts with optional filters - following API.md spec
  async listAccounts(params?: {
    search?: string;  // Changed from 'q' to 'search' per API.md
    tier?: string;
    page?: number;    // Changed from 'offset' to 'page' per API.md
    size?: number;    // Changed from 'limit' to 'size' per API.md
  }): Promise<AccountListResponse> {
    // Filter out undefined values and 'all' tier
    const cleanParams: Record<string, string | number> = {};
    
    if (params?.search) cleanParams.search = params.search;
    if (params?.tier && params.tier !== 'all') cleanParams.tier = params.tier;
    if (params?.page) cleanParams.page = params.page;
    if (params?.size) cleanParams.size = params.size;

    const response = await apiClient.get('/accounts/', { params: cleanParams });
    return response.data;
  }

  // Get single account by ID
  async getAccount(accountId: string): Promise<AccountDetailResponse> {
    const response = await apiClient.get(`${this.baseURL}/${accountId}`);
    return response.data;
  }

  // Create new account - following API.md spec
  async createAccount(data: AccountCreate): Promise<{ status_code: number; account_id: string; message: string }> {
    // Transform form data to API format per API.md
    try {
      const response = await apiClient.post('/accounts/', data);
      return response.data;
    } catch (error: any) {
      throw error;
    }
  }

  // Update existing account - following API.md spec
  async updateAccount(
    accountId: string,
    data: AccountUpdate
  ): Promise<{ status_code: number; message: string }> {
    // Transform form data to API format - send only provided fields per API.md
    const updateData: Partial<AccountUpdate> = {};

    if (data.client_name !== undefined) updateData.client_name = data.client_name;
    if (data.company_website !== undefined)
      updateData.company_website = data.company_website || null;
    if (data.client_address !== undefined) {
      updateData.client_address = data.client_address ? {
        line1: data.client_address.line1 || '',
        line2: data.client_address.line2 || null,
        city: data.client_address.city || null,
        pincode: data.client_address.pincode || null,
      } : null;
    }
    if (data.client_type !== undefined) updateData.client_type = data.client_type;
    if (data.market_sector !== undefined) updateData.market_sector = data.market_sector || null;
    if (data.notes !== undefined) updateData.notes = data.notes || null;


    try {
      const response = await apiClient.put(`${this.baseURL}/${accountId}`, updateData);
      return response.data;
    } catch (error: any) {
      // If CORS blocks PUT, try using PATCH method instead
      if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
        try {
          const response = await apiClient.patch(`${this.baseURL}/${accountId}`, updateData);
          return response.data;
        } catch (patchError: any) {

          // Last resort: POST with method override
          const response = await apiClient.post(`${this.baseURL}/${accountId}`, {
            ...updateData,
            _method: 'PUT',
          });
          return response.data;
        }
      }
      throw error;
    }
  }

  // Delete account - following API.md spec
  async deleteAccount(accountId: string): Promise<{ status_code: number; message: string }> {
    const response = await apiClient.delete(`${this.baseURL}/${accountId}`);
    return response.data;
  }

  // Add secondary contact to account - following API.md spec
  async addContact(
    accountId: string,
    contact: ContactAddRequest
  ): Promise<{ status_code: number; contact_id: string; message: string }> {

    const response = await apiClient.post(`${this.baseURL}/${accountId}/contacts`, contact);
    return response.data;
  }

  // Get all contacts for account - following API.md spec
  async getContacts(accountId: string): Promise<ContactListResponse> {
    const response = await apiClient.get(`${this.baseURL}/${accountId}/contacts`);
    return response.data;
  }

  // Update contact (primary or secondary) - following API.md spec
  async updateContact(
    accountId: string,
    contactId: string,
    contact: ContactUpdateRequest
  ): Promise<{ status_code: number; message: string }> {
    const contactData = {
      name: contact.name,
      email: contact.email,
      phone: contact.phone,
      title: contact.title || null,
    };

    const response = await apiClient.put(
      `${this.baseURL}/${accountId}/contacts/${contactId}`,
      contactData
    );
    return response.data;
  }

  // Delete secondary contact - following API.md spec (primary contacts cannot be deleted)
  async deleteContact(
    accountId: string,
    contactId: string
  ): Promise<{ status_code: number; message: string }> {
    const response = await apiClient.delete(`${this.baseURL}/${accountId}/contacts/${contactId}`);
    return response.data;
  }

  // Promote secondary contact to primary - following API.md spec
  async promoteContactToPrimary(
    accountId: string,
    contactId: string
  ): Promise<{ status_code: number; message: string }> {
    try {
      // Step 1: Get current account details to get primary and secondary contacts
      const accountDetails = await this.getAccount(accountId);
      const currentPrimary = accountDetails.primary_contact;
      
      // Find the secondary contact to promote by contact_id
      const secondaryToPromote = accountDetails.secondary_contacts?.find(
        contact => contact.contact_id === contactId
      );
      
      if (!secondaryToPromote) {
        throw new Error('Secondary contact not found');
      }

      // Step 2: Delete the secondary contact that we're promoting
      await this.deleteContact(accountId, contactId);

      // Step 3: Update the primary contact with the secondary contact's data
      await apiClient.put(`${this.baseURL}/${accountId}`, {
        primary_contact: {
          name: secondaryToPromote.name,
          email: secondaryToPromote.email,
          phone: secondaryToPromote.phone,
          title: secondaryToPromote.title || null,
        }
      });

      // Step 4: Add the old primary contact as a new secondary contact (if it existed)
      if (currentPrimary && typeof currentPrimary === 'object') {
        await this.addContact(accountId, {
          contact: {
            name: currentPrimary.name,
            email: currentPrimary.email,
            phone: currentPrimary.phone,
            title: currentPrimary.title || undefined,
          }
        });
      }

      return {
        status_code: 200,
        message: 'Contact promoted to primary successfully'
      };
    } catch (error: any) {
      throw error;
    }
  }

  // Enhanced methods for AI features

  // Enrich account data using AI scraping
  async enrichAccountData(website: string): Promise<{
    company_name?: string;
    industry?: string;
    description?: string;
    contacts?: Array<{
      name?: string;
      email?: string;
      phone?: string;
      title?: string;
    }>;
    address?: {
      line1?: string;
      line2?: string;
      city?: string;
      state?: string;
      pincode?: number;
    };
  }> {
    try {
      // Use the existing scraperApi service
      const scrapeResult = await scraperApi.scraper([website]);
      const result = scrapeResult.results[0];

      if (result.error) {
        throw new Error(`Scraping failed: ${result.error}`);
      }

      const info = result.info;
      if (!info) {
        return {};
      }

      // Transform scraped data to our expected format
      return {
        company_name: info.name || undefined,
        contacts:
          info.email?.map((email, index) => ({
            email,
            phone: info.phone?.[index] || '',
            name: `Contact ${index + 1}`,
          })) || [],
        address: info.address
          ? {
              line1: info.address.line1 || undefined,
              line2: info.address.line2 || undefined,
              city: info.address.city || undefined,
              state: info.address.state || undefined,
              pincode: info.address.pincode ? Number(info.address.pincode) : undefined,
            }
          : undefined,
      };
    } catch (error) {
      throw error;
    }
  }

  // Get AI insights for account
  async getAIInsights(accountId: string): Promise<{
    health_score: number;
    opportunities: string[];
    risks: string[];
    recommendations: string[];
    tier_suggestion?: string;
    tier_reasoning?: string;
  }> {
    try {
      const response = await apiClient.get(`${this.baseURL}/${accountId}/ai-insights`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // Generate account report
  async generateAccountReport(accountId: string): Promise<{
    report_url: string;
    report_id: string;
  }> {
    try {
      const response = await apiClient.post(`${this.baseURL}/${accountId}/generate-report`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export const accountsApi = new AccountsApiService();
