import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useAccountDetail, useAccounts } from '@/hooks/useAccounts';
import { TabType, AccountFormData, AccountStatsCard } from './AccountDetailsPage.types';
import { MOCK_RECENT_ACTIVITY } from './AccountDetailsPage.constants';

export function useAccountDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // State
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<AccountFormData | null>(null);

  // API calls
  const { accountDetail: account, isAccountDetailLoading: isLoading, accountDetailError: error } = useAccountDetail(id || '');
  const { updateAccount, isUpdating } = useAccounts();

  // Initialize form data when account loads
  useEffect(() => {
    if (account && !formData) {
      setFormData({
        client_name: account.client_name || '',
        client_type: account.client_type || '',
        market_sector: account.market_sector || '',
        client_address: typeof account.client_address === 'string' 
          ? account.client_address 
          : account.client_address?.line1 || '',
        city: typeof account.client_address === 'object' && account.client_address
          ? String(account.client_address?.city || '') 
          : '',
        state: typeof account.client_address === 'object' && account.client_address
          ? String(account.client_address?.state || '') 
          : '',
        zip_code: typeof account.client_address === 'object' 
          ? String(account.client_address?.pincode || '') 
          : '',
        company_website: account.company_website || '',
        hosting_area: '',
        msa_in_place: false,
        account_approver: '',
        approval_date_time: '',
      });
    }
  }, [account, formData]);

  // Computed values

  const statsCards: AccountStatsCard[] = useMemo(() => {
    if (!account) return [];
    
    return [
      {
        id: 'total-value',
        title: 'Total Value',
        value: account.total_value ? `$${account.total_value}M` : '$0M',
        icon: 'DollarSign',
      },
      {
        id: 'opportunities',
        title: 'Opportunities',
        value: account.opportunities || 0,
        icon: 'Target',
      },
      {
        id: 'last-contact',
        title: 'Last Contact',
        value: account.last_contact 
          ? new Date(account.last_contact).toLocaleDateString()
          : 'Never',
        icon: 'Calendar',
      },
      {
        id: 'client-type',
        title: 'Client Type',
        value: account.client_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'N/A',
        icon: 'Award',
      },
    ];
  }, [account]);

  // Handlers
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
  };

  const handleEditToggle = () => {
    if (isEditing && formData) {
      // Reset form data when canceling edit
      if (account) {
        setFormData({
          client_name: account.client_name || '',
          client_type: account.client_type || '',
          market_sector: account.market_sector || '',
          client_address: typeof account.client_address === 'string' 
            ? account.client_address 
            : account.client_address?.line1 || '',
          city: typeof account.client_address === 'object' && account.client_address
            ? String(account.client_address?.city || '') 
            : '',
          state: typeof account.client_address === 'object' && account.client_address
            ? String(account.client_address?.state || '') 
            : '',
          zip_code: typeof account.client_address === 'object' 
            ? String(account.client_address?.pincode || '') 
            : '',
          company_website: account.company_website || '',
          hosting_area: '',
          msa_in_place: false,
          account_approver: '',
          approval_date_time: '',
        });
      }
    }
    setIsEditing(!isEditing);
  };

  const handleFormChange = (field: keyof AccountFormData, value: any) => {
    if (!formData) return;
    
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  const handleSaveChanges = async () => {
    if (!account?.account_id || !formData) return;

    try {
      await updateAccount({
        accountId: account.account_id,
        data: {
          client_name: formData.client_name,
          client_type: formData.client_type as any,
          market_sector: formData.market_sector,
          client_address: {
            line1: formData.client_address,
            line2: '',
            pincode: parseInt(formData.zip_code) || 0,
          },
          company_website: formData.company_website || undefined,
          notes: undefined,
        },
      });

      toast({
        title: 'Account Updated',
        description: 'Account information has been updated successfully.',
      });

      setIsEditing(false);
    } catch (error: any) {
      console.error('Error updating account:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail?.message || 'Failed to update account. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const handleBackToAccounts = () => {
    navigate('/module/accounts');
  };

  return {
    // Data
    account,
    isLoading,
    error,
    activeTab,
    isEditing,
    formData,
    statsCards,
    recentActivity: MOCK_RECENT_ACTIVITY,

    // Actions
    handleTabChange,
    handleEditToggle,
    handleFormChange,
    handleSaveChanges,
    handleBackToAccounts,

    // Status
    isUpdating,
  };
}
