import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useAccounts } from '@/hooks/useAccounts';
import { AccountStatsData, FilterState } from './AccountsPage.types';
import { AccountCreate, AccountListItem } from '@/types/accounts';
import { ClientType } from './components/CreateAccountModal/CreateAccountModal.types';

export function useAccountsPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Local state
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    tier: 'all',
  });
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Use the real accounts hook
  const {
    useAccountsList,
    createAccount,
    deleteAccount,
    isCreating,
    isDeleting,
  } = useAccounts();

  // Use real API data with current filters
  const accountsQuery = useAccountsList({
    search: filters.search || undefined,
    tier: filters.tier !== 'all' ? filters.tier : undefined,
  });

  const accounts = accountsQuery?.data?.accounts || [];
  const isLoading = accountsQuery?.isLoading || false;

  // API handles filtering, so we use accounts directly
  const filteredAccounts = accounts;

  // Calculate stats from accounts data
  const stats: AccountStatsData = useMemo(() => {
    if (filteredAccounts.length === 0) {
      return {
        totalAccounts: 0,
        aiHealthScore: 0,
        highRiskCount: 0,
        growingCount: 0,
        totalValue: '$0',
      };
    }

    const totalAccounts = filteredAccounts.length;
    const aiHealthScore = Math.round(
      filteredAccounts.reduce((sum, acc) => sum + (acc.ai_health_score || 0), 0) / totalAccounts
    );
    // Since these fields don't exist in AccountListItem, we'll set them to 0
    const highRiskCount = 0;
    const growingCount = 0;
    
    // Calculate total value from actual account values
    const totalValueNumber = filteredAccounts.reduce((sum, acc) => {
      return sum + (acc.total_value || 0);
    }, 0);
    const totalValue = `$${totalValueNumber.toFixed(1)}M`;

    return {
      totalAccounts,
      aiHealthScore,
      highRiskCount,
      growingCount,
      totalValue,
    };
  }, [filteredAccounts]);

  // Handlers
  const handleSearchChange = (search: string) => {
    setFilters(prev => ({ ...prev, search }));
  };

  const handleTierChange = (tier: FilterState['tier']) => {
    setFilters(prev => ({ ...prev, tier }));
  };

  const handleCreateAccount = () => {
    setIsCreateModalOpen(true);
  };

  const handleCreateAccountSubmit = async (formData: AccountCreate) => {
    try {
      console.log('🚀 handleCreateAccountSubmit: Form data received:', formData);
      
      // Transform the form data to match the API expected format
      // Client type is already in the correct format since we're using the enum

      
      console.log('🔄 handleCreateAccountSubmit: Transformed API data:', formData);
      
      // Use the real API call
      await createAccount(formData);
      
      // Only close modal and show success message if API call succeeds
      toast({
        title: 'Account Created Successfully',
        description: `${formData.client_name} has been added to your accounts.`,
      });
      setIsCreateModalOpen(false);
    } catch (error: any) {
      console.error('Error creating account:', error);
      
      // Show more specific error message from API if available
      const errorMessage = error.response?.data?.detail?.[0]?.msg 
        || error.response?.data?.message 
        || 'There was an error creating the account. Please try again.';
      
      toast({
        title: 'Error Creating Account',
        description: errorMessage,
        variant: 'destructive',
      });
      
      // Re-throw error so the form component can handle it
      throw error;
    }
  };

  const handleAccountClick = (accountId: string) => {
    navigate(`/module/accounts/${accountId}`);
  };

  const handleExport = (format: string) => {
    toast({
      title: `Exporting to ${format.toUpperCase()}`,
      description: `Account data is being exported to ${format} format.`,
    });
  };

  const handleStatClick = (statId: string) => {
    // Handle stat card clicks - could filter or navigate
    console.log('Stat clicked:', statId);
  };

  return {
    // Data
    accounts: filteredAccounts,
    stats,
    filters,
    isLoading,
    isCreateModalOpen,
    
    // Actions
    handleSearchChange,
    handleTierChange,
    handleCreateAccount,
    handleCreateAccountSubmit,
    handleAccountClick,
    handleExport,
    handleStatClick,
    setIsCreateModalOpen,
    
    // Status
    isCreating: isCreating || false,
    isDeleting: isDeleting || false,
  };
}
