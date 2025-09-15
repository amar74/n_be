import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useAccounts } from '@/hooks/useAccounts';
import { AccountData, AccountStatsData, FilterState, CreateAccountFormData } from './AccountsPage.types';
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

  const handleCreateAccountSubmit = async (formData: CreateAccountFormData) => {
    try {
      // TODO: Replace with actual API call when backend is ready
      // For now, we'll simulate account creation with mock data
      const newAccount: AccountData = {
        accountId: `ACC-${String(accounts.length + 1).padStart(3, '0')}`,
        name: formData.clientName,
        clientMarketSector: formData.clientMarketSector,
        location: `${formData.city}, ${formData.state}`,
        internalContact: formData.primaryContact || 'Contact TBD',
        hostingArea: formData.hostingArea || 'Office TBD',
        clientType: formData.clientType as 'Tire 1' | 'Tire 2' | 'Tire 3',
        msaInPlace: formData.msaInPlace === 'Yes',
        totalOpportunities: 0,
        totalValue: '$0',
        lastContact: new Date().toISOString().split('T')[0],
        aiHealthScore: Math.floor(Math.random() * 40) + 60, // Random score between 60-100
        healthTrend: 'stable' as const,
        riskLevel: 'low' as const,
        website: formData.companyWebsite,
      };

      // In a real implementation, this would be:
      // await createAccount(newAccount);
      
      // For now, just show success message
      toast({
        title: 'Account Created Successfully',
        description: `${formData.clientName} has been added to your accounts.`,
      });

      setIsCreateModalOpen(false);
    } catch (error) {
      toast({
        title: 'Error Creating Account',
        description: 'There was an error creating the account. Please try again.',
        variant: 'destructive',
      });
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
