import React, { useState, useEffect } from 'react';
import { Link, NavigateFunction, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useToast } from '@/hooks/use-toast';
import { useAccounts } from '@/hooks/useAccounts';
import { scraperApi, ApiError } from '@/services/api/scraperApi';
import {
  CreateAccountFormData,
  UpdateAccountFormData,
  AccountListItem,
  AccountDetailResponse,
  CLIENT_TIERS,
  MARKET_SECTORS,
  ContactFormData,
} from '@/types/accounts';
import {
  Building2,
  ArrowLeft,
  Search,
  Download,
  Plus,
  ChevronDown,
  MapPin,
  Users,
  LogOut,
  Filter,
  Eye,
  MoreHorizontal,
  Building,
  Phone,
  Mail,
  Award,
  FileText,
  Brain,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Lightbulb,
  RefreshCw,
  Globe,
  Settings,
  Activity,
  DollarSign,
  BarChart3,
  MessageSquare,
  Calendar,
  Sparkles,
  Zap,
  Cpu,
  UserPlus,
  Trash2,
  Bot,
} from 'lucide-react';
import { Logo } from '@/components/ui/logo';
import UniversalChatbot from '@/components/UniversalChatbot';

// Legacy interface for backwards compatibility with existing UI
interface AccountData {
  accountId: string;
  name: string;
  clientMarketSector: string;
  location: string;
  internalContact: string;
  hostingArea: string;
  clientType: 'Tier 1' | 'Tier 2' | 'Tier 3';
  msaInPlace: boolean;
  totalOpportunities: number;
  totalValue: string;
  lastContact: string;
  aiHealthScore?: number;
  healthTrend?: 'up' | 'down' | 'stable';
  riskLevel?: 'low' | 'medium' | 'high';
  lastAIAnalysis?: string;
  revenueGrowth?: number;
  communicationFrequency?: number;
  winRate?: number;
  website?: string;
  suggestedOpportunities?: string[];
  dataQualityScore?: number;
  lastDataUpdate?: string;
  aiInsights?: {
    summary: string;
    actionItems: string[];
    opportunities: string[];
    risks: string[];
  };
}

export function Accounts() {
  const navigate = useNavigate();
  const { toast } = useToast();

  // Use the new useAccounts hook
  const {
    useAccountsList,
    createAccount,
    deleteAccount,
    enrichAccountData,
    isCreating,
    isDeleting,
    isEnriching,
  } = useAccounts();

  // Local UI state
  const [searchQuery, setSearchQuery] = useState('');
  const [tierFilter, setTierFilter] = useState('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const userEmail = localStorage.getItem('userEmail') || 'user@example.com';

  // Form state for creating/editing accounts
  const [accountForm, setAccountForm] = useState<CreateAccountFormData>({
    client_name: '',
    company_website: '',
    client_address: {
      line1: '',
      line2: '',
      pincode: undefined,
    },
    client_type: 'tier_2',
    market_sector: '',
    contacts: [],
  });

  // AI-powered assistance state
  const [isAIAnalyzing, setIsAIAnalyzing] = useState(false);
  const [aiInsightsDialogOpen, setAiInsightsDialogOpen] = useState(false);
  const [selectedAccountForInsights, setSelectedAccountForInsights] = useState<AccountData | null>(
    null
  );
  const [contactOptions, setContactOptions] = useState<string[]>([]);
  const [isCustomSelected, setIsCustomSelected] = useState(false);
  const [customContact, setCustomContact] = useState('');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const [dataEnrichmentResults, setDataEnrichmentResults] = useState<any>(null);
  const [showAITieringSuggestion, setShowAITieringSuggestion] = useState(false);
  const [aiSuggestedTier, setAiSuggestedTier] = useState('');
  const [aiTieringReason, setAiTieringReason] = useState('');
  const [isGeneratingProjectSheet, setIsGeneratingProjectSheet] = useState(false);

  // Use the accounts list query with filters
  const {
    data: accountsResponse,
    isLoading: isLoadingAccounts,
    error: accountsError,
  } = useAccountsList({
    search: searchQuery || undefined,
    tier: tierFilter !== 'all' ? tierFilter : undefined,
    size: 50,
  });

  const apiAccounts = accountsResponse?.accounts || [];

  // Wrapper functions for backwards compatibility with existing UI code
  const handleCreateAccount = async () => {
    console.log('Creating account with data:', accountForm);

    // Validate required fields
    if (!accountForm.client_name || !accountForm.client_type) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in Client Name and Client Type.',
        variant: 'destructive',
      });
      return;
    }

    // Validate required address fields
    if (!accountForm.client_address.line1) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in Address Line 1.',
        variant: 'destructive',
      });
      return;
    }

    // Validate primary contact - must have at least one contact with required fields
    const primaryContact = accountForm.contacts?.[0];
    if (!primaryContact || !primaryContact.name || !primaryContact.email || !primaryContact.phone) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in Primary Contact Name, Email, and Phone (minimum 10 characters).',
        variant: 'destructive',
      });
      return;
    }

    // Validate phone number length (API requires minimum 10 characters)
    if (primaryContact.phone.length < 10) {
      toast({
        title: 'Validation Error',
        description: 'Primary Contact Phone must be at least 10 characters long.',
        variant: 'destructive',
      });
      return;
    }

    try {
      await createAccount(accountForm);

      // Reset form on success
      setAccountForm({
        client_name: '',
        company_website: '',
        client_address: {
          line1: '',
          line2: '',
          pincode: undefined,
        },
        client_type: 'tier_2',
        market_sector: '',
        contacts: [],
      });

      // Close dialog
      setIsCreateDialogOpen(false);
      setShowAISuggestions(false);
    } catch (error) {
      console.error('Failed to create account:', error);
    }
  };

  const handleDeleteAccount = async (accountId: string) => {
    try {
      await deleteAccount(accountId);
    } catch (error) {
      console.error('Failed to delete account:', error);
    }
  };

  const handleEnrichAccountData = async (website: string) => {
    try {
      const result = await enrichAccountData(website);
      setDataEnrichmentResults(result);
      return result;
    } catch (error) {
      console.error('Failed to enrich account data:', error);
      throw error;
    }
  };

  // Wrapper function for account ID-based enrichment
  const handleEnrichAccountDataById = async (accountId: string) => {
    try {
      // Find the account to get its website
      const account = filteredAccounts?.find(acc => acc.account_id === accountId);
      if (!account?.company_website) {
        toast({
          title: 'No Website Found',
          description: 'This account does not have a website URL to enrich data from.',
          variant: 'destructive',
        });
        return;
      }

      const result = await enrichAccountData(String(account.company_website));
      setDataEnrichmentResults(result);
    } catch (error) {
      console.error('Failed to enrich account data:', error);
      toast({
        title: 'Enrichment Failed',
        description: 'Failed to enrich account data. Please try again.',
        variant: 'destructive',
      });
    }
  };

  // AI Agent Management state
  const [agentPanelOpen, setAgentPanelOpen] = useState(false);
  const [createAgentOpen, setCreateAgentOpen] = useState(false);
  const [agents, setAgents] = useState([
    {
      id: 'agent-001',
      name: 'Account Analyst Pro',
      type: 'Account Management',
      status: 'active',
      tasks: ['Monitor account health', 'Generate insights', 'Update contact info'],
      modules: ['accounts', 'opportunities'],
      lastActive: '2 minutes ago',
      tasksCompleted: 147,
      avatar: '🤖',
      capabilities: ['Data Analysis', 'Report Generation', 'Contact Management'],
      autonomyLevel: 'High',
    },
    {
      id: 'agent-002',
      name: 'Survey Coordinator',
      type: 'Client Engagement',
      status: 'active',
      tasks: ['Schedule surveys', 'Follow up responses', 'Generate reports'],
      modules: ['client-surveys', 'accounts'],
      lastActive: '5 minutes ago',
      tasksCompleted: 89,
      avatar: '📊',
      capabilities: ['Survey Management', 'Client Communication', 'Analytics'],
      autonomyLevel: 'Medium',
    },
    {
      id: 'agent-003',
      name: 'Opportunity Hunter',
      type: 'Business Development',
      status: 'idle',
      tasks: ['Research new opportunities', 'Qualify leads', 'Update pipeline'],
      modules: ['opportunities', 'accounts'],
      lastActive: '1 hour ago',
      tasksCompleted: 234,
      avatar: '����',
      capabilities: ['Lead Generation', 'Market Research', 'Pipeline Management'],
      autonomyLevel: 'High',
    },
  ]);

  const [newAgent, setNewAgent] = useState({
    name: '',
    type: '',
    modules: [],
    tasks: [],
    capabilities: [],
    autonomyLevel: 'Medium',
    avatar: '🤖',
  });

  // Form state for creating new accounts
  const [newAccount, setNewAccount] = useState({
    clientName: '',
    clientAddress: '',
    primaryContact: '',
    contactEmail: '',
    marketSector: '',
    clientType: '',
    hostingArea: '',
    msaInPlace: '',
    website: '',
  });

  const [isLoadingAddress, setIsLoadingAddress] = useState(false);
  const [addressLookupTimeout, setAddressLookupTimeout] = useState<NodeJS.Timeout | null>(null);

  const handleExport = (format: string) => {
    toast({
      title: `Exporting to ${format.toUpperCase()}`,
      description: `Account data is being exported to ${format} format.`,
    });
  };

  const handleViewAccount = (accountId: string) => {
    navigate(`/module/accounts/${accountId}`);
  };

  const getHostingAreaLabel = (value: string) => {
    const areaMap: { [key: string]: string } = {
      northeast: 'Northeast Office',
      southeast: 'Southeast Office',
      midwest: 'Midwest Office',
      southwest: 'Southwest Office',
      west: 'West Office',
    };
    return areaMap[value] || 'Office TBD';
  };

  const getClientTypeLabel = (value: string) => {
    const typeMap: { [key: string]: string } = {
      tier1: 'Tier 1',
      tier2: 'Tier 2',
      tier3: 'Tier 3',
    };
    return typeMap[value] || 'Tier 3';
  };

  // AI-powered address lookup function

  // Simulate AI address lookup with comprehensive company database

  // Debounced client name change handler

  // Cleanup timeout on unmount
  React.useEffect(() => {
    return () => {
      if (addressLookupTimeout) {
        clearTimeout(addressLookupTimeout);
      }
    };
  }, [addressLookupTimeout]);

  // AI-powered health score calculation
  const calculateAIHealthScore = (account: AccountData): number => {
    if (account.aiHealthScore) return account.aiHealthScore;

    let score = 50; // Base score

    // Revenue growth factor (0-25 points)
    const revenueGrowth = account.revenueGrowth || 0;
    score += Math.min(25, Math.max(-25, revenueGrowth * 1.5));

    // Communication frequency factor (0-20 points)
    const commFreq = account.communicationFrequency || 5;
    score += Math.min(20, commFreq * 2);

    // Win rate factor (0-25 points)
    const winRate = account.winRate || 50;
    score += (winRate - 50) * 0.5;

    // Client tier factor (0-15 points)
    const tierBonus = { 'Tier 1': 15, 'Tier 2': 10, 'Tier 3': 5 };
    score += tierBonus[account.clientType] || 0;

    // MSA bonus (0-10 points)
    if (account.msaInPlace) score += 10;

    // Days since last contact penalty
    const lastContactDate = new Date(account.lastContact);
    const daysSinceContact = Math.floor(
      (new Date().getTime() - lastContactDate.getTime()) / (1000 * 3600 * 24)
    );
    score -= Math.min(15, daysSinceContact * 0.5);

    return Math.min(100, Math.max(0, Math.round(score)));
  };

  // AI-powered intelligent tiering suggestion
  const suggestAITiering = async (
    marketSector: string,
    potentialRevenue?: string,
    website?: string
  ) => {
    setIsAIAnalyzing(true);

    try {
      // Simulate AI analysis delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      let suggestedTier = 'tier3';
      let reasoning = '';

      // Market sector analysis
      const highValueSectors = ['Transportation', 'Infrastructure', 'Healthcare', 'Education'];
      const mediumValueSectors = ['Environmental', 'Aviation', 'Government'];

      if (highValueSectors.includes(marketSector)) {
        if (potentialRevenue && parseFloat(potentialRevenue.replace(/[$M,]/g, '')) > 5) {
          suggestedTier = 'tier1';
          reasoning = `High-value ${marketSector} sector with significant revenue potential. Strategic tier classification recommended.`;
        } else {
          suggestedTier = 'tier2';
          reasoning = `${marketSector} sector shows strong potential. Mid-tier classification suggested for focused development.`;
        }
      } else if (mediumValueSectors.includes(marketSector)) {
        suggestedTier = 'tier2';
        reasoning = `${marketSector} sector presents moderate opportunities. Mid-tier approach recommended.`;
      } else {
        suggestedTier = 'tier3';
        reasoning = 'Standard tier classification suggested. Monitor for growth opportunities.';
      }

      // Website analysis (if provided)
      if (website) {
        const governmentDomains = ['.gov', '.edu', '.org'];
        if (governmentDomains.some(domain => website.includes(domain))) {
          if (suggestedTier === 'tier3') suggestedTier = 'tier2';
          reasoning +=
            ' Government/institutional domain indicates stability and long-term potential.';
        }
      }

      setAiSuggestedTier(suggestedTier);
      setAiTieringReason(reasoning);
      setShowAITieringSuggestion(true);

      toast({
        title: '🤖 AI Tiering Analysis Complete',
        description: `Suggested tier: ${suggestedTier.replace('tier', 'Tier ').charAt(0).toUpperCase() + suggestedTier.slice(1)}`,
      });
    } catch (error) {
      toast({
        title: 'AI Analysis Error',
        description: 'Unable to complete tiering analysis. Please select manually.',
        variant: 'destructive',
      });
    } finally {
      setIsAIAnalyzing(false);
    }
  };

  // Smart website data population
  const populateFromWebsite = async (websiteUrl: string) => {
    if (!websiteUrl || !websiteUrl.includes('.')) return;
    console.log('Populating from website:', websiteUrl);

    setIsLoadingAddress(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Enhanced website scraping simulation
      const websiteData = await analyzeWebsite(websiteUrl);

      if (websiteData?.name || websiteData?.address) {
        const formattedAddress = [
          websiteData?.address?.line1,
          websiteData?.address?.city,
          websiteData?.address?.state,
        ]
          .filter(Boolean)
          .join(', ');

        setAccountForm(prev => ({
          ...prev,
          client_name: typeof websiteData?.name === 'string' ? websiteData.name : prev.client_name,
          client_address: {
            line1: formattedAddress || prev.client_address.line1,
            line2: prev.client_address.line2,
            pincode: websiteData?.address?.pincode
              ? Number(websiteData.address.pincode)
              : prev.client_address.pincode,
          },
          // Keep user's website input
          company_website: prev.company_website,
        }));

        // Trigger AI tiering suggestion if we have enough data
        // if (websiteData.sector) {
        //   await suggestAITiering(websiteData.sector, websiteData.revenue, websiteUrl);
        // }

        toast({
          title: '🤖 Website Data Extracted',
          description: `Auto-populated ${Object.values(websiteData).filter(v => v).length} fields from website`,
        });
      }
    } catch (error) {
      toast({
        title: 'Website Analysis Error',
        description: 'Unable to extract data from website. Please fill manually.',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingAddress(false);
    }
  };

  // Enhanced website scraping simulation
  const analyzeWebsite = async (website: string) => {
    if (!website || !website.includes('.')) return;

    setIsAnalyzing(true);

    try {
      const scrapeResult = await scraperApi.scraper([website]);

      const result = scrapeResult.results[0];

      if (result.error) {
        throw new Error(`Scraping failed: ${result.error}`);
      }

      setShowAISuggestions(true);

      toast({
        title: '🔍 Website Analysis Complete',
        description: 'We auto-filled fields using real data from the website.',
      });

      console.log('Scraped info:', result.info);
      return result.info;
    } catch (error) {
      if (error instanceof ApiError) {
        toast({
          title: 'Scraper Error',
          description: `API error: ${error.detail?.[0]?.msg || 'Unknown error'}`,
          variant: 'destructive',
        });
      } else {
        toast({
          title: 'Analysis Failed',
          description: (error as Error).message || 'An unknown error occurred.',
          variant: 'destructive',
        });
      }

      console.error('Website analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'Tier 1':
        return 'bg-green-50 text-green-700 border-green-300';
      case 'Tier 2':
        return 'bg-blue-50 text-blue-700 border-blue-300';
      case 'Tier 3':
        return 'bg-orange-50 text-orange-700 border-orange-300';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-300';
    }
  };

  // AI Health Score visualization helpers
  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getHealthTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-blue-600" />;
    }
  };

  const getRiskLevelColor = (risk: string) => {
    switch (risk) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Helper functions to link data from respective modules
  const getLinkedHealthScore = (account: AccountData): number => {
    // Link to client survey data - calculate based on survey responses
    const surveyResponses = {
      'ACC-001': { avgRating: 4.2, responseRate: 67, satisfactionScore: 85 },
      'ACC-002': { avgRating: 3.8, responseRate: 45, satisfactionScore: 76 },
      'ACC-003': { avgRating: 4.5, responseRate: 78, satisfactionScore: 90 },
      'ACC-004': { avgRating: 3.1, responseRate: 33, satisfactionScore: 62 },
      'ACC-005': { avgRating: 3.4, responseRate: 40, satisfactionScore: 68 },
      'ACC-006': { avgRating: 2.9, responseRate: 25, satisfactionScore: 58 },
    };

    const surveyData = surveyResponses[account.accountId as keyof typeof surveyResponses];
    if (surveyData) {
      // Calculate health score based on survey metrics: 40% rating, 30% response rate, 30% satisfaction
      const ratingScore = (surveyData.avgRating / 5) * 40;
      const responseScore = (surveyData.responseRate / 100) * 30;
      const satisfactionWeight = (surveyData.satisfactionScore / 100) * 30;
      return Math.round(ratingScore + responseScore + satisfactionWeight);
    }

    // Fallback to default calculation if no survey data
    return calculateAIHealthScore(account);
  };

  const getLinkedWinRate = (account: AccountData): number => {
    // Link to proposals module - calculate based on completed proposals
    const proposalData = {
      'ACC-001': { totalProposals: 8, wonProposals: 7, value: '$8.5M' },
      'ACC-002': { totalProposals: 6, wonProposals: 4, value: '$5.2M' },
      'ACC-003': { totalProposals: 10, wonProposals: 8, value: '$8.7M' },
      'ACC-004': { totalProposals: 5, wonProposals: 2, value: '$4.1M' },
      'ACC-005': { totalProposals: 3, wonProposals: 2, value: '$1.5M' },
      'ACC-006': { totalProposals: 4, wonProposals: 1, value: '$2.8M' },
    };

    const proposals = proposalData[account.accountId as keyof typeof proposalData];
    if (proposals) {
      return Math.round((proposals.wonProposals / proposals.totalProposals) * 100);
    }

    // Fallback to account's existing win rate
    return account.winRate || 65;
  };

  const getLinkedRevenueGrowth = (account: AccountData): number => {
    // Link to finance module - calculate based on financial data
    const financeData = {
      'ACC-001': { currentYearRevenue: 8500000, previousYearRevenue: 7200000 },
      'ACC-002': { currentYearRevenue: 5200000, previousYearRevenue: 4800000 },
      'ACC-003': { currentYearRevenue: 8700000, previousYearRevenue: 7500000 },
      'ACC-004': { currentYearRevenue: 4100000, previousYearRevenue: 4200000 },
      'ACC-005': { currentYearRevenue: 1500000, previousYearRevenue: 1420000 },
      'ACC-006': { currentYearRevenue: 2800000, previousYearRevenue: 2750000 },
    };

    const finance = financeData[account.accountId as keyof typeof financeData];
    if (finance) {
      const growth =
        ((finance.currentYearRevenue - finance.previousYearRevenue) / finance.previousYearRevenue) *
        100;
      return Math.round(growth * 10) / 10; // Round to 1 decimal place
    }

    // Fallback to account's existing revenue growth
    return account.revenueGrowth || 0;
  };

  // Enhanced client name change handler with AI suggestions

  // Website change handler with smart population
  const handleWebsiteChange = (value: string) => {
    setAccountForm(prev => ({ ...prev, company_website: value }));

    // Auto-populate from website if it looks valid
    if (value.includes('.') && value.length > 5) {
      setTimeout(() => {
        populateFromWebsite(value);
      }, 1500);
    }
  };

  // Filter API accounts based on search and tier
  const filteredAccounts = apiAccounts.filter((account: AccountListItem) => {
    const addressText =
      typeof account.client_address === 'string'
        ? account.client_address
        : account.client_address
          ? `${account.client_address.line1} ${account.client_address.line2 || ''} ${account.client_address.pincode || ''}`
          : '';

    const matchesSearch =
      account.client_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      account.market_sector?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      addressText.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (account.primary_contact && typeof account.primary_contact === 'object'
        ? account.primary_contact.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          account.primary_contact.email?.toLowerCase().includes(searchQuery.toLowerCase())
        : false);

    const matchesTier =
      tierFilter === 'all' ||
      (tierFilter === 'tier_1' && account.client_type === 'tier_1') ||
      (tierFilter === 'tier_2' && account.client_type === 'tier_2') ||
      (tierFilter === 'tier_3' && account.client_type === 'tier_3');

    return matchesSearch && matchesTier;
  });

  // Adapter function to convert API data to legacy format for backwards compatibility
  const convertToLegacyFormat = (account: AccountListItem): AccountData => ({
    accountId: account.account_id,
    name: account.client_name,
    clientMarketSector: account.market_sector || '',
    location:
      typeof account.client_address === 'string'
        ? account.client_address
        : account.client_address
          ? `${account.client_address.line1}${account.client_address.line2 ? ', ' + account.client_address.line2 : ''}${account.client_address.pincode ? ' - ' + account.client_address.pincode : ''}`
          : 'Location TBD',
    internalContact:
      account.primary_contact && typeof account.primary_contact === 'object'
        ? account.primary_contact.name || 'Contact TBD'
        : 'Contact TBD',
    hostingArea: 'Hosting Area', // Not available in API, default value
    clientType:
      account.client_type === 'tier_1'
        ? 'Tier 1'
        : account.client_type === 'tier_2'
          ? 'Tier 2'
          : 'Tier 3',
    msaInPlace: false, // Not available in API, default value
    totalOpportunities: (account as any).total_opportunities || 0,
    totalValue: account.total_value ? `$${account.total_value.toLocaleString()}` : '$0',
    lastContact: account.last_contact || new Date().toISOString().split('T')[0],
    aiHealthScore: account.ai_health_score || undefined,
    healthTrend: 'stable' as 'up' | 'down' | 'stable', // Default value since not available in API
    riskLevel: 'low' as 'low' | 'medium' | 'high', // Default value since not available in API
  });

  // Convert filtered accounts to legacy format for components
  const legacyFilteredAccounts: AccountData[] = filteredAccounts.map(convertToLegacyFormat);

  // Agent Management Functions
  const createAgent = () => {
    if (!newAgent.name || !newAgent.type) {
      toast({
        title: 'Missing Information',
        description: 'Please provide agent name and type.',
        variant: 'destructive',
      });
      return;
    }

    const agent = {
      id: `agent-${Date.now()}`,
      ...newAgent,
      status: 'idle',
      lastActive: 'Just created',
      tasksCompleted: 0,
    };

    setAgents([...agents, agent]);
    setNewAgent({
      name: '',
      type: '',
      modules: [],
      tasks: [],
      capabilities: [],
      autonomyLevel: 'Medium',
      avatar: '🤖',
    });
    setCreateAgentOpen(false);

    toast({
      title: 'Agent Created',
      description: `${agent.name} is ready to start working.`,
    });
  };

  const activateAgent = (agentId: string) => {
    setAgents(
      agents.map(agent =>
        agent.id === agentId ? { ...agent, status: 'active', lastActive: 'Just now' } : agent
      )
    );

    toast({
      title: 'Agent Activated',
      description: 'Agent is now processing tasks.',
    });
  };

  const deactivateAgent = (agentId: string) => {
    setAgents(agents.map(agent => (agent.id === agentId ? { ...agent, status: 'idle' } : agent)));

    toast({
      title: 'Agent Deactivated',
      description: 'Agent has been paused.',
    });
  };

  const deleteAgent = (agentId: string) => {
    setAgents(agents.filter(agent => agent.id !== agentId));
    toast({
      title: 'Agent Deleted',
      description: 'Agent has been removed from the system.',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'idle':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-[#FCFCFC] font-['Inter',_system-ui,_-apple-system,_sans-serif]">
      <div className="max-w-7xl mx-auto px-8 sm:px-12 lg:px-16 py-12">
        {/* Back Button */}
        <div className="mb-12">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-6 py-3 text-[#1D1D1F] hover:text-[#0D9488] hover:bg-[#F3F4F6] rounded-md transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 font-medium overflow-wrap-break-word"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            <span>Back to Dashboard</span>
          </Link>
        </div>
        {/* Header Section */}
        <div className="flex justify-between items-center mb-12">
          <div>
            <h2 className="text-4xl font-medium text-[#1D1D1F] mb-4 text-center overflow-wrap-break-word">
              My Accounts
            </h2>
            <p className="text-lg text-[#1D1D1F] leading-relaxed font-normal overflow-wrap-break-word">
              Manage client accounts and relationship data
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-6">
            <ActionsDropdown handleExport={handleExport} />

            <Link to="/modules/accounts-user-permissions">
              <Button
                variant="outline"
                className="bg-[#0D9488] hover:bg-[#0D9488]/90 text-white border-[#0D9488] px-6 py-3 rounded-md font-medium transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 active:scale-99 shadow-[0_4px_16px_rgba(0,0,0,0.08)]"
              >
                Permissions
              </Button>
            </Link>

            <Link to="/client-surveys">
              <Button
                variant="outline"
                className="bg-[#F59E0B] hover:bg-[#F59E0B]/90 text-white border-[#F59E0B] px-6 py-3 rounded-md font-medium transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 active:scale-99 shadow-[0_4px_16px_rgba(0,0,0,0.08)]"
              >
                <FileText className="h-4 w-4 mr-2" />
                Client Surveys
              </Button>
            </Link>

            <CreateNewAccountModal
              accountForm={accountForm}
              setAccountForm={setAccountForm}
              aiSuggestedTier={aiSuggestedTier}
              aiTieringReason={aiTieringReason}
              handleCreateAccount={handleCreateAccount}
              handleWebsiteChange={handleWebsiteChange}
              isAIAnalyzing={isAIAnalyzing}
              isCreateDialogOpen={isCreateDialogOpen}
              isLoadingAddress={isLoadingAddress}
              setIsCreateDialogOpen={setIsCreateDialogOpen}
              setShowAITieringSuggestion={setShowAITieringSuggestion}
              showAITieringSuggestion={showAITieringSuggestion}
              toast={toast}
            />

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="outline"
                  className="bg-[#FCFCFC] hover:bg-[#F3F4F6] border-[#EFF1F3] text-[#1D1D1F] px-6 py-3 rounded-md font-medium transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 active:scale-99 shadow-[0_4px_16px_rgba(0,0,0,0.08)]"
                >
                  <Filter className="h-4 w-4 mr-2" />
                  {tierFilter === 'all'
                    ? 'All Accounts'
                    : tierFilter === 'tier1'
                      ? 'Tier 1 Accounts'
                      : tierFilter === 'tier2'
                        ? 'Tier 2 Accounts'
                        : 'Tier 3 Accounts'}
                  <ChevronDown className="h-4 w-4 ml-2" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-48">
                <DropdownMenuItem
                  onClick={() => setTierFilter('all')}
                  className={tierFilter === 'all' ? 'bg-blue-50 text-blue-700' : ''}
                >
                  <Building className="h-4 w-4 mr-2" />
                  All Accounts
                  {tierFilter === 'all' && <CheckCircle className="h-4 w-4 ml-auto" />}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => setTierFilter('tier1')}
                  className={tierFilter === 'tier1' ? 'bg-blue-50 text-blue-700' : ''}
                >
                  <Award className="h-4 w-4 mr-2 text-yellow-600" />
                  Tier 1 Accounts
                  {tierFilter === 'tier1' && <CheckCircle className="h-4 w-4 ml-auto" />}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => setTierFilter('tier2')}
                  className={tierFilter === 'tier2' ? 'bg-blue-50 text-blue-700' : ''}
                >
                  <Award className="h-4 w-4 mr-2 text-blue-600" />
                  Tier 2 Accounts
                  {tierFilter === 'tier2' && <CheckCircle className="h-4 w-4 ml-auto" />}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => setTierFilter('tier3')}
                  className={tierFilter === 'tier3' ? 'bg-blue-50 text-blue-700' : ''}
                >
                  <Award className="h-4 w-4 mr-2 text-green-600" />
                  Tier 3 Accounts
                  {tierFilter === 'tier3' && <CheckCircle className="h-4 w-4 ml-auto" />}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="mb-12">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-[#1D1D1F] h-5 w-5" />
            <Input
              placeholder="how can I help?"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-12 pr-6 py-4 bg-[#F3F4F6] border-[#EFF1F3] text-[#1D1D1F] placeholder-[#1D1D1F]/60 rounded-md font-medium transition-all duration-300 ease-in-out focus:bg-[#FCFCFC] focus:border-[#0D9488] shadow-[0_4px_16px_rgba(0,0,0,0.08)] overflow-wrap-break-word"
            />
          </div>
        </div>

        {/* Account Summary Stats with AI Insights */}

        <InfoCards
          accounts={legacyFilteredAccounts}
          calculateAIHealthScore={calculateAIHealthScore}
          setSearchQuery={setSearchQuery}
        />

        {/* Accounts Grid */}

        <IndivisualAccountCard
          calculateAIHealthScore={calculateAIHealthScore}
          enrichAccountData={handleEnrichAccountDataById}
          filteredAccounts={legacyFilteredAccounts}
          getHealthScoreBackground={getHealthScoreBackground}
          getHealthScoreColor={getHealthScoreColor}
          getHealthTrendIcon={getHealthTrendIcon}
          getRiskLevelColor={getRiskLevelColor}
          getTierColor={getTierColor}
          handleViewAccount={handleViewAccount}
          isEnrichingData={isEnriching}
          isGeneratingProjectSheet={isGeneratingProjectSheet}
          navigate={navigate}
          setAiInsightsDialogOpen={setAiInsightsDialogOpen}
          setSelectedAccountForInsights={setSelectedAccountForInsights}
        />

        {/* AI Insights Summary Banner */}
        <Card className="border-2 border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50 mt-6">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-purple-100 p-3 rounded-full">
                  <Cpu className="h-8 w-8 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
                    🤖 AI Account Intelligence
                    <Badge variant="outline" className="bg-purple-100 text-purple-700">
                      Active
                    </Badge>
                  </h3>
                  <p className="text-slate-600">
                    AI continuously monitors {apiAccounts.length} accounts, analyzing{' '}
                    {legacyFilteredAccounts.filter(a => a.riskLevel === 'high').length} high-risk
                    relationships and{' '}
                    {legacyFilteredAccounts.filter(a => a.healthTrend === 'up').length} growth
                    opportunities.
                  </p>
                </div>
              </div>
              <div className="text-right">
                <Button
                  variant="outline"
                  onClick={() => {
                    // Find the account with the highest risk that needs attention
                    // const highRiskAccount = accounts.find(a => a.riskLevel === 'high');
                    // if (highRiskAccount) {
                    //   setSelectedAccountForInsights(highRiskAccount);
                    //   setAiInsightsDialogOpen(true);
                    // } else {
                    //   toast({
                    //     title: '🎉 All Accounts Healthy',
                    //     description: 'No high-risk accounts require immediate attention.',
                    //   });
                    // }
                  }}
                  className="bg-purple-100 hover:bg-purple-200 text-purple-700 border-purple-300"
                >
                  <Target className="h-4 w-4 mr-2" />
                  Review Priority Accounts
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default Accounts;

interface ActionsDropdownProps {
  handleExport: (format: string) => void;
}

function ActionsDropdown({ handleExport }: ActionsDropdownProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className="bg-[#FCFCFC] hover:bg-[#F3F4F6] border-[#EFF1F3] text-[#1D1D1F] px-6 py-3 rounded-md font-medium transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 active:scale-99 shadow-[0_4px_16px_rgba(0,0,0,0.08)]"
        >
          Actions
          <ChevronDown className="h-4 w-4 ml-2" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={() => handleExport('excel')}>
          <Download className="h-4 w-4 mr-2" />
          Export to Excel
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleExport('csv')}>
          <Download className="h-4 w-4 mr-2" />
          Export to CSV
        </DropdownMenuItem>
        <DropdownMenuItem>
          <Filter className="h-4 w-4 mr-2" />
          Resize Columns to Fit Screen
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

interface CreateNewAccountModalProps {
  accountForm: CreateAccountFormData;
  setAccountForm: React.Dispatch<React.SetStateAction<CreateAccountFormData>>;
  aiSuggestedTier: string;
  aiTieringReason: string;
  handleCreateAccount: () => void;
  handleWebsiteChange: (value: string) => void;
  isAIAnalyzing: boolean;
  isCreateDialogOpen: boolean;
  isLoadingAddress: boolean;
  setIsCreateDialogOpen: React.Dispatch<React.SetStateAction<boolean>>;
  setShowAITieringSuggestion: React.Dispatch<React.SetStateAction<boolean>>;
  showAITieringSuggestion: boolean;
  toast: any;
}

function CreateNewAccountModal({
  accountForm,
  setAccountForm,
  aiSuggestedTier,
  aiTieringReason,
  handleCreateAccount,
  handleWebsiteChange,
  isAIAnalyzing,
  isCreateDialogOpen,
  isLoadingAddress,
  setIsCreateDialogOpen,
  setShowAITieringSuggestion,
  showAITieringSuggestion,
  toast,
}: CreateNewAccountModalProps) {
  return (
    <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
      <DialogTrigger asChild>
        <Button className="bg-[#0D9488] hover:bg-[#0D9488]/90 text-white px-8 py-3 rounded-md font-medium transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 active:scale-99 shadow-[0_4px_16px_rgba(0,0,0,0.08)]">
          <Plus className="h-4 w-4 mr-2" />
          Create Account
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] bg-white">
        <DialogHeader>
          <DialogTitle>Create New Account</DialogTitle>
          <DialogDescription>Add a new client account to your portfolio</DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-4">
          <div className="md:col-span-2">
            <Label htmlFor="website">🤖 Company Website (AI Smart Population)</Label>
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                id="website"
                placeholder="https://company.com (AI will extract company info)"
                value={accountForm.company_website || ''}
                onChange={e => handleWebsiteChange(e.target.value)}
                className="pl-10"
              />
              {isLoadingAddress && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                </div>
              )}
            </div>
            {accountForm.company_website &&
              accountForm.company_website.includes('.') &&
              !isLoadingAddress && (
                <p className="text-xs text-purple-600 mt-1 flex items-center gap-1">
                  <Bot className="h-3 w-3" />
                  AI will analyze website and populate fields automatically...
                </p>
              )}
          </div>

          <div>
            <Label htmlFor="client-name">Client Name *</Label>
            <div className="relative">
              <Input
                id="client-name"
                placeholder="Company name"
                value={accountForm.client_name}
                onChange={e => setAccountForm(prev => ({ ...prev, client_name: e.target.value }))}
              />
              {isAIAnalyzing && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Brain className="h-4 w-4 text-purple-600 animate-pulse" />
                </div>
              )}
            </div>
            {accountForm.client_name.length >= 3 && !isLoadingAddress && (
              <p className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                AI analyzing for intelligent suggestions...
              </p>
            )}
          </div>
          <div>
            <Label htmlFor="client-address">
              Client Address
              {accountForm.client_address.line1 && !isLoadingAddress && (
                <span className="text-green-600 text-xs ml-2">🤖 Auto-filled by AI</span>
              )}
            </Label>
            <Input
              id="client-address"
              placeholder="Billing address (auto-filled by AI)"
              value={accountForm.client_address.line1}
              onChange={e =>
                setAccountForm(prev => ({
                  ...prev,
                  client_address: { ...prev.client_address, line1: e.target.value },
                }))
              }
              className={
                accountForm.client_address.line1 && !isLoadingAddress
                  ? 'bg-green-50 border-green-200'
                  : ''
              }
            />
          </div>
          {/* Primary Contact Section */}
          <div className="md:col-span-2">
            <h3 className="text-lg font-semibold text-[#1D1D1F] mb-4 flex items-center gap-2">
              <Users className="h-5 w-5 text-[#0D9488]" />
              Primary Contact Information
            </h3>
          </div>
          
          <div>
            <Label htmlFor="primary-contact-name">Primary Contact Name *</Label>
            <Input
              id="primary-contact-name"
              placeholder="Contact full name"
              value={accountForm.contacts?.[0]?.name || ''}
              onChange={e =>
                setAccountForm(prev => ({
                  ...prev,
                  contacts: [
                    {
                      name: e.target.value,
                      email: prev.contacts?.[0]?.email || '',
                      phone: prev.contacts?.[0]?.phone || '',
                      title: prev.contacts?.[0]?.title || '',
                    },
                    ...(prev.contacts?.slice(1) || [])
                  ],
                }))
              }
            />
          </div>

          <div>
            <Label htmlFor="primary-contact-email">Primary Contact Email *</Label>
            <Input
              id="primary-contact-email"
              type="email"
              placeholder="email@company.com"
              value={accountForm.contacts?.[0]?.email || ''}
              onChange={e =>
                setAccountForm(prev => ({
                  ...prev,
                  contacts: [
                    {
                      name: prev.contacts?.[0]?.name || '',
                      email: e.target.value,
                      phone: prev.contacts?.[0]?.phone || '',
                      title: prev.contacts?.[0]?.title || '',
                    },
                    ...(prev.contacts?.slice(1) || [])
                  ],
                }))
              }
            />
          </div>

          <div>
            <Label htmlFor="primary-contact-phone">Primary Contact Phone *</Label>
            <Input
              id="primary-contact-phone"
              type="tel"
              placeholder="+1 (555) 123-4567"
              value={accountForm.contacts?.[0]?.phone || ''}
              onChange={e =>
                setAccountForm(prev => ({
                  ...prev,
                  contacts: [
                    {
                      name: prev.contacts?.[0]?.name || '',
                      email: prev.contacts?.[0]?.email || '',
                      phone: e.target.value,
                      title: prev.contacts?.[0]?.title || '',
                    },
                    ...(prev.contacts?.slice(1) || [])
                  ],
                }))
              }
            />
          </div>

          <div>
            <Label htmlFor="primary-contact-title">Primary Contact Title</Label>
            <Input
              id="primary-contact-title"
              placeholder="Job title (optional)"
              value={accountForm.contacts?.[0]?.title || ''}
              onChange={e =>
                setAccountForm(prev => ({
                  ...prev,
                  contacts: [
                    {
                      name: prev.contacts?.[0]?.name || '',
                      email: prev.contacts?.[0]?.email || '',
                      phone: prev.contacts?.[0]?.phone || '',
                      title: e.target.value,
                    },
                    ...(prev.contacts?.slice(1) || [])
                  ],
                }))
              }
            />
          </div>

          {/* Secondary Contacts Section */}
          <div className="md:col-span-2">
            <h3 className="text-lg font-semibold text-[#1D1D1F] mb-4 flex items-center gap-2">
              <UserPlus className="h-5 w-5 text-[#6B7280]" />
              Secondary Contacts (Optional)
            </h3>
            
            {/* Display existing secondary contacts */}
            {accountForm.contacts && accountForm.contacts.length > 1 && (
              <div className="space-y-3 mb-4">
                {accountForm.contacts.slice(1).map((contact, index) => (
                  <div key={index} className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                    <div className="flex justify-between items-start">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 flex-1">
                        <Input
                          placeholder="Contact name"
                          value={contact.name}
                          onChange={e => {
                            const updatedContacts = [...(accountForm.contacts || [])];
                            updatedContacts[index + 1] = { ...contact, name: e.target.value };
                            setAccountForm(prev => ({ ...prev, contacts: updatedContacts }));
                          }}
                        />
                        <Input
                          type="email"
                          placeholder="Email"
                          value={contact.email}
                          onChange={e => {
                            const updatedContacts = [...(accountForm.contacts || [])];
                            updatedContacts[index + 1] = { ...contact, email: e.target.value };
                            setAccountForm(prev => ({ ...prev, contacts: updatedContacts }));
                          }}
                        />
                        <Input
                          type="tel"
                          placeholder="Phone"
                          value={contact.phone}
                          onChange={e => {
                            const updatedContacts = [...(accountForm.contacts || [])];
                            updatedContacts[index + 1] = { ...contact, phone: e.target.value };
                            setAccountForm(prev => ({ ...prev, contacts: updatedContacts }));
                          }}
                        />
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          const updatedContacts = accountForm.contacts?.filter((_, i) => i !== index + 1) || [];
                          setAccountForm(prev => ({ ...prev, contacts: updatedContacts }));
                        }}
                        className="ml-2 text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            {/* Add secondary contact button */}
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                const newContact = { name: '', email: '', phone: '', title: '' };
                setAccountForm(prev => ({
                  ...prev,
                  contacts: [...(prev.contacts || []), newContact],
                }));
              }}
              className="w-full border-dashed border-gray-300 text-gray-600 hover:border-gray-400 hover:text-gray-800"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Secondary Contact
            </Button>
          </div>

          {/* Company Information */}
          <div className="md:col-span-2">
            <h3 className="text-lg font-semibold text-[#1D1D1F] mb-4 flex items-center gap-2">
              <Building className="h-5 w-5 text-[#0D9488]" />
              Company Information
            </h3>
          </div>

          <div>
            <Label htmlFor="market-sector" className="bg-white">
              Client Market Sector *
            </Label>
            <Select
              value={accountForm.market_sector || ''}
              onValueChange={value => setAccountForm(prev => ({ ...prev, market_sector: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select sector" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="Transportation">Transportation</SelectItem>
                <SelectItem value="Infrastructure">Infrastructure</SelectItem>
                <SelectItem value="Environmental">Environmental</SelectItem>
                <SelectItem value="Aviation">Aviation</SelectItem>
                <SelectItem value="Education">Education</SelectItem>
                <SelectItem value="Healthcare">Healthcare</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="client-type" className="flex items-center gap-2">
              Client Type *
              {showAITieringSuggestion && (
                <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-300">
                  <Brain className="h-3 w-3 mr-1" />
                  AI Suggestion
                </Badge>
              )}
            </Label>
            <Select
              value={accountForm.client_type}
              onValueChange={value => {
                setAccountForm(prev => ({
                  ...prev,
                  client_type: value as 'tier_1' | 'tier_2' | 'tier_3',
                }));
                if (showAITieringSuggestion && value !== aiSuggestedTier) {
                  setShowAITieringSuggestion(false);
                }
              }}
            >
              <SelectTrigger
                className={
                  showAITieringSuggestion && accountForm.client_type === aiSuggestedTier
                    ? 'border-purple-300 bg-purple-50'
                    : ''
                }
              >
                <SelectValue placeholder="Select tier" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem
                  value="tier_1"
                  className={aiSuggestedTier === 'tier_1' ? 'bg-purple-50 font-medium' : ''}
                >
                  Tier 1 {aiSuggestedTier === 'tier_1' && '🤖 AI Recommended'}
                </SelectItem>
                <SelectItem
                  value="tier_2"
                  className={aiSuggestedTier === 'tier_2' ? 'bg-purple-50 font-medium' : ''}
                >
                  Tier 2 {aiSuggestedTier === 'tier_2' && '🤖 AI Recommended'}
                </SelectItem>
                <SelectItem
                  value="tier_3"
                  className={aiSuggestedTier === 'tier_3' ? 'bg-purple-50 font-medium' : ''}
                >
                  Tier 3 {aiSuggestedTier === 'tier_3' && '🤖 AI Recommended'}
                </SelectItem>
              </SelectContent>
            </Select>
            {showAITieringSuggestion && aiTieringReason && (
              <div className="mt-2 p-2 bg-purple-50 border border-purple-200 rounded-md">
                <p className="text-xs text-purple-700 flex items-start gap-1">
                  <Lightbulb className="h-3 w-3 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong>AI Analysis:</strong> {aiTieringReason}
                  </span>
                </p>
                <div className="flex gap-2 mt-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    className="text-xs h-6 px-2 bg-purple-100 border-purple-300 hover:bg-purple-200"
                    onClick={() => {
                      setAccountForm(prev => ({
                        ...prev,
                        client_type: aiSuggestedTier as 'tier_1' | 'tier_2' | 'tier_3',
                      }));
                      toast({
                        title: 'AI Suggestion Applied',
                        description: `Client type updated to ${aiSuggestedTier.replace('tier_', 'Tier ')}`,
                      });
                    }}
                  >
                    <Zap className="h-3 w-3 mr-1" />
                    Apply AI Suggestion
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    className="text-xs h-6 px-2"
                    onClick={() => setShowAITieringSuggestion(false)}
                  >
                    Dismiss
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* <div>
            <Label htmlFor="hosting-area">Hosting Area/Office</Label>
            <Select
              value={newAccount.hostingArea}
              onValueChange={value => setNewAccount(prev => ({ ...prev, hostingArea: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select office" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="northeast">Northeast Office</SelectItem>
                <SelectItem value="southeast">Southeast Office</SelectItem>
                <SelectItem value="midwest">Midwest Office</SelectItem>
                <SelectItem value="southwest">Southwest Office</SelectItem>
                <SelectItem value="west">West Office</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="msa">MSA in Place</Label>
            <Select
              value={newAccount.msaInPlace}
              onValueChange={value => setNewAccount(prev => ({ ...prev, msaInPlace: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="yes">Yes</SelectItem>
                <SelectItem value="no">No</SelectItem>
              </SelectContent>
            </Select>
          </div> */}
          <div>
            <Label htmlFor="pincode">Postal Code</Label>
            <Input
              id="pincode"
              placeholder="Postal/ZIP code"
              type="number"
              value={accountForm.client_address.pincode || ''}
              onChange={e =>
                setAccountForm(prev => ({
                  ...prev,
                  client_address: {
                    ...prev.client_address,
                    pincode: e.target.value ? Number(e.target.value) : undefined,
                  },
                }))
              }
            />
          </div>
        </div>
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleCreateAccount}>Create Account</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface InfoCardsProps {
  accounts: AccountData[];
  calculateAIHealthScore: (account: AccountData) => number;
  setSearchQuery: React.Dispatch<React.SetStateAction<string>>;
}

function InfoCards({ accounts, calculateAIHealthScore, setSearchQuery }: InfoCardsProps) {
  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-16">
        <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
            <Building className="h-10 w-10 text-[#0D9488] mx-auto mb-4" />
            <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">
              Total Accounts
            </h4>
            <p className="text-3xl font-medium text-[#0D9488] mt-2">{accounts.length}</p>
          </CardContent>
        </Card>

        <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
            <Brain className="h-10 w-10 text-[#0D9488] mx-auto mb-4" />
            <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">
              AI Health Score
            </h4>
            <p className="text-3xl font-medium text-[#0D9488] mt-2">
              {Math.round(
                accounts.reduce((sum, acc) => sum + calculateAIHealthScore(acc), 0) /
                  accounts.length
              )}
              %
            </p>
            <p className="text-sm text-[#1D1D1F]/70 mt-1">Average</p>
          </CardContent>
        </Card>

        <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
            <AlertTriangle className="h-10 w-10 text-[#F59E0B] mx-auto mb-4" />
            <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">High Risk</h4>
            <p className="text-3xl font-medium text-[#F59E0B] mt-2">
              {accounts.filter(a => a.riskLevel === 'high').length}
            </p>
            <p className="text-sm text-[#1D1D1F]/70 mt-1">Require Attention</p>
          </CardContent>
        </Card>

        <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
            <TrendingUp className="h-10 w-10 text-[#0D9488] mx-auto mb-4" />
            <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">Growing</h4>
            <p className="text-3xl font-medium text-[#0D9488] mt-2">
              {accounts.filter(a => a.healthTrend === 'up').length}
            </p>
            <p className="text-sm text-[#1D1D1F]/70 mt-1">Positive Trend</p>
          </CardContent>
        </Card>

        <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg">
          <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
            <DollarSign className="h-10 w-10 text-[#F59E0B] mx-auto mb-4" />
            <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">
              Total Value
            </h4>
            <p className="text-3xl font-medium text-[#F59E0B] mt-2">
              $
              {accounts
                .reduce((sum, acc) => sum + parseFloat(acc.totalValue.replace(/[$M,]/g, '')), 0)
                .toFixed(1)}
              M
            </p>
            <p className="text-sm text-[#1D1D1F]/70 mt-1">Portfolio</p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}

interface IndivisualAccountCardProps {
  calculateAIHealthScore: (account: AccountData) => number;
  enrichAccountData: (accountId: string) => Promise<void>;
  filteredAccounts: AccountData[];
  getHealthScoreBackground: (
    score: number
  ) =>
    | 'bg-green-50 border-green-200'
    | 'bg-yellow-50 border-yellow-200'
    | 'bg-red-50 border-red-200';
  getHealthScoreColor: (score: number) => 'text-green-600' | 'text-yellow-600' | 'text-red-600';
  getHealthTrendIcon: (trend: string) => React.JSX.Element;
  getRiskLevelColor: (
    risk: string
  ) =>
    | 'bg-green-100 text-green-800'
    | 'bg-yellow-100 text-yellow-800'
    | 'bg-red-100 text-red-800'
    | 'bg-gray-100 text-gray-800';
  getTierColor: (
    tier: string
  ) =>
    | 'bg-green-50 text-green-700 border-green-300'
    | 'bg-blue-50 text-blue-700 border-blue-300'
    | 'bg-orange-50 text-orange-700 border-orange-300'
    | 'bg-gray-50 text-gray-700 border-gray-300';
  handleViewAccount: (accountId: string) => void;
  isEnrichingData: boolean;
  isGeneratingProjectSheet: boolean;
  navigate: NavigateFunction;
  setAiInsightsDialogOpen: React.Dispatch<React.SetStateAction<boolean>>;
  setSelectedAccountForInsights: React.Dispatch<React.SetStateAction<AccountData | null>>;
}

function IndivisualAccountCard({
  calculateAIHealthScore,
  enrichAccountData,
  filteredAccounts,
  getHealthScoreBackground,
  getHealthScoreColor,
  getHealthTrendIcon,
  getRiskLevelColor,
  getTierColor,
  handleViewAccount,
  isEnrichingData,
  isGeneratingProjectSheet,
  navigate,
  setAiInsightsDialogOpen,
  setSelectedAccountForInsights,
}: IndivisualAccountCardProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-16">
      {filteredAccounts.map(account => {
        const healthScore = calculateAIHealthScore(account);
        return (
          <Card
            key={account.accountId}
            className={`border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] hover:border-[#0D9488] transition-all duration-300 ease-in-out cursor-pointer hover:transform hover:-translate-y-0.5 hover:shadow-lg active:scale-99 ${getHealthScoreBackground(healthScore)}`}
            onClick={() => handleViewAccount(account.accountId)}
          >
            <CardHeader className="p-8">
              <div className="flex justify-between items-start">
                <div className="flex items-center space-x-4">
                  <div className="bg-[#0D9488]/10 p-3 rounded-md relative">
                    <Building className="h-6 w-6 text-[#0D9488]" />
                    {account.riskLevel === 'high' && (
                      <div className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full animate-pulse" />
                    )}
                  </div>
                  <div>
                    <CardTitle className="text-xl font-medium text-[#1D1D1F] overflow-wrap-break-word">
                      {account.name}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-2 text-[#1D1D1F]/70 overflow-wrap-break-word">
                      {account.accountId}
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger>
                            <Brain className="h-4 w-4 text-[#0D9488]" />
                          </TooltipTrigger>
                          <TooltipContent>AI-powered insights available</TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {/* AI Health Score */}
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <div
                          className={`flex items-center space-x-1 px-2 py-1 rounded-lg border ${getHealthScoreBackground(healthScore)}`}
                        >
                          <Cpu className="h-3 w-3 text-purple-600" />
                          <span className={`text-sm font-bold ${getHealthScoreColor(healthScore)}`}>
                            {healthScore}%
                          </span>
                          {getHealthTrendIcon(account.healthTrend || 'stable')}
                        </div>
                      </TooltipTrigger>
                      <TooltipContent>
                        <div className="max-w-xs">
                          <p className="font-semibold">AI Health Score: {healthScore}%</p>
                          <p className="text-xs mt-1">
                            Based on revenue growth ({account.revenueGrowth}%), win rate (
                            {account.winRate}%), and communication frequency
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Last analyzed: {account.lastAIAnalysis}
                          </p>
                        </div>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" onClick={e => e.stopPropagation()}>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem>
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={e => {
                          e.stopPropagation();
                          setSelectedAccountForInsights(account);
                          setAiInsightsDialogOpen(true);
                        }}
                      >
                        <Brain className="h-4 w-4 mr-2" />
                        AI Insights & Analysis
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={e => {
                          e.stopPropagation();
                          enrichAccountData(account.accountId);
                        }}
                        disabled={isEnrichingData}
                      >
                        <RefreshCw
                          className={`h-4 w-4 mr-2 ${isEnrichingData ? 'animate-spin' : ''}`}
                        />
                        {isEnrichingData ? 'Enriching Data...' : 'Enrich Account Data'}
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={e => {
                          e.stopPropagation();
                          // generateAIProjectSheet(account.accountId);
                        }}
                        disabled={isGeneratingProjectSheet}
                      >
                        <FileText className="h-4 w-4 mr-2" />
                        Generate AI Project Sheet
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={e => {
                          e.stopPropagation();
                          navigate(`/module/accounts/${account.accountId}/qualifications`);
                        }}
                      >
                        <Award className="h-4 w-4 mr-2" />
                        View Qualifications
                      </DropdownMenuItem>
                      <DropdownMenuItem>Edit Account</DropdownMenuItem>
                      <DropdownMenuItem>
                        <Phone className="h-4 w-4 mr-2" />
                        Contact
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-8 pt-4">
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <MapPin className="h-5 w-5 text-[#1D1D1F]/60" />
                  <span className="text-base text-[#1D1D1F] font-normal overflow-wrap-break-word">
                    {account.location}
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <Users className="h-5 w-5 text-[#1D1D1F]/60" />
                  <span className="text-base text-[#1D1D1F] font-normal overflow-wrap-break-word">
                    {account.internalContact}
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <Building2 className="h-5 w-5 text-[#1D1D1F]/60" />
                  <span className="text-base text-[#1D1D1F] font-normal overflow-wrap-break-word">
                    {account.hostingArea}
                  </span>
                </div>

                <div className="flex justify-between items-center pt-4">
                  <Badge variant="outline" className={getTierColor(account.clientType)}>
                    {account.clientType}
                  </Badge>
                  <Badge
                    variant="outline"
                    className="bg-[#F3F4F6] text-[#1D1D1F] border-[#EFF1F3] px-3 py-1 rounded-md font-medium overflow-wrap-break-word"
                  >
                    {account.clientMarketSector}
                  </Badge>
                </div>

                {/* AI Risk Assessment */}
                {account.riskLevel && (
                  <div className="flex items-center justify-between pt-2 border-t">
                    <span className="text-xs text-gray-500">Risk Level</span>
                    <Badge variant="outline" className={getRiskLevelColor(account.riskLevel)}>
                      {account.riskLevel.charAt(0).toUpperCase() + account.riskLevel.slice(1)} Risk
                    </Badge>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 pt-2 border-t">
                  <div>
                    <p className="text-xs text-gray-500">Opportunities</p>
                    <p className="font-semibold text-blue-600">{account.totalOpportunities}</p>
                    {account.winRate && (
                      <p className="text-xs text-gray-500">Win Rate: {account.winRate}%</p>
                    )}
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Total Value</p>
                    <p className="font-semibold text-green-600">{account.totalValue}</p>
                    {account.revenueGrowth && (
                      <p
                        className={`text-xs ${account.revenueGrowth > 0 ? 'text-green-600' : 'text-red-600'}`}
                      >
                        {account.revenueGrowth > 0 ? '+' : ''}
                        {account.revenueGrowth}% growth
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Last Contact: {account.lastContact}</span>
                  {account.msaInPlace && (
                    <Badge variant="outline" className="bg-green-50 text-green-700">
                      MSA
                    </Badge>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
