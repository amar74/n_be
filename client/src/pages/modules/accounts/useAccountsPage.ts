import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useAccounts } from '@/hooks/useAccounts';
import { AccountData, AccountStatsData, FilterState } from './AccountsPage.types';
import { MOCK_ACCOUNTS } from './AccountsPage.constants';

export function useAccountsPage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Local state
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    tier: 'all',
  });
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  // Use the existing accounts hook (if available) or fallback to mock data
  const {
    useAccountsList,
    createAccount,
    deleteAccount,
    isCreating,
    isDeleting,
  } = useAccounts?.() || {};

  // For now, use mock data - replace with real API call later
  const accounts: AccountData[] = MOCK_ACCOUNTS;
  const isLoading = false;

  // Filter accounts based on current filters
  const filteredAccounts = useMemo(() => {
    return accounts.filter((account) => {
      const matchesSearch = filters.search === '' || 
        account.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        account.clientMarketSector.toLowerCase().includes(filters.search.toLowerCase()) ||
        account.location.toLowerCase().includes(filters.search.toLowerCase());

      const matchesTier = filters.tier === 'all' || 
        (filters.tier === 'tire_1' && account.clientType === 'Tire 1') ||
        (filters.tier === 'tire_2' && account.clientType === 'Tire 2') ||
        (filters.tier === 'tire_3' && account.clientType === 'Tire 3');

      return matchesSearch && matchesTier;
    });
  }, [accounts, filters]);

  // Calculate stats from filtered accounts
  const stats: AccountStatsData = useMemo(() => {
    const totalAccounts = filteredAccounts.length;
    const aiHealthScore = Math.round(
      filteredAccounts.reduce((sum, acc) => sum + (acc.aiHealthScore || 0), 0) / totalAccounts
    );
    const highRiskCount = filteredAccounts.filter(acc => acc.riskLevel === 'high').length;
    const growingCount = filteredAccounts.filter(acc => acc.healthTrend === 'up').length;
    const totalValue = '$92.6M'; // Calculated from all accounts

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
    handleAccountClick,
    handleExport,
    handleStatClick,
    setIsCreateModalOpen,
    
    // Status
    isCreating: isCreating || false,
    isDeleting: isDeleting || false,
  };
}
