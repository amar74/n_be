import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useAccounts } from '@/hooks/useAccounts';
import { AccountStatsData, FilterState } from './AccountsPage.types';
import { AccountCreate, AccountListItem } from '@/types/accounts';
import { ClientType } from './components/CreateAccountModal/CreateAccountModal.types';
import { tr } from 'date-fns/locale';

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
    isLoading,
    accountsList,
    createAccount,
    fetchAccounts,
    isCreating,
    isDeleting,
    createErrors,
  } = useAccounts({eager: true});

  const accounts = accountsList?.accounts || [];
  // Use real API data with current filters
 


  // API handles filtering, so we use accounts directly

  // Calculate stats from accounts data
  const stats: AccountStatsData = useMemo(() => {
    if (accounts.length === 0) {
      return {
        totalAccounts: 0,
        aiHealthScore: 0,
        highRiskCount: 0,
        growingCount: 0,
        totalValue: '$0',
      };
    }

    const totalAccounts = accounts.length;
    const aiHealthScore = Math.round(
      accounts.reduce((sum, acc) => sum + (acc.ai_health_score || 0), 0) / totalAccounts
    );
    // Since these fields don't exist in AccountListItem, we'll set them to 0
    const highRiskCount = 0;
    const growingCount = 0;
    
    // Calculate total value from actual account values
    const totalValueNumber = accounts.reduce((sum, acc) => {
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
  }, [accounts]);

  // Handlers
  const handleSearchChange = (search: string) => {
    setFilters(prev => ({ ...prev, search }));
  };

  const handleTierChange = (tier: FilterState['tier']) => {
    fetchAccounts(tier === 'all' ? undefined : { tier });
    setFilters(prev => ({ ...prev, tier }));
  };

  const handleCreateAccount = () => {
    setIsCreateModalOpen(true);
  };

  const handleCreateAccountSubmit = async (formData: AccountCreate) => {
    try {
      // Use the real API call
      await createAccount(formData);
      
      // Only close modal and show success message if API call succeeds
      toast({
        title: 'Account Created Successfully',
        description: `${formData.client_name} has been added to your accounts.`,
      });
      setIsCreateModalOpen(false);
    } catch (error: any) {
      // Show specific error message from API if available
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
    // TODO: Implement stat card click handling (filtering or navigation)
  };

  return {
    // Data
    accounts,
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
    createErrors,
  };
}
