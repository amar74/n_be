import { AccountData } from './AccountsPage.types';

export const ACCOUNT_TIERS = {
  TIRE_1: 'Tire 1',
  TIRE_2: 'Tire 2', 
  TIRE_3: 'Tire 3',
} as const;

export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
} as const;

export const HEALTH_TRENDS = {
  UP: 'up',
  DOWN: 'down',
  STABLE: 'stable',
} as const;

export const FILTER_OPTIONS = [
  { value: 'all', label: 'All Accounts' },
  { value: 'tire_1', label: 'Tire 1 Accounts' },
  { value: 'tire_2', label: 'Tire 2 Accounts' },
  { value: 'tire_3', label: 'Tire 3 Accounts' },
] as const;

export const STATS_CARDS = [
  {
    id: 'total-accounts',
    title: 'Total Accounts',
    icon: 'Building',
    color: '#ed8a09',
  },
  {
    id: 'ai-health-score',
    title: 'AI Health Score',
    icon: 'Brain',
    color: '#ed8a09',
    suffix: '% Average',
  },
  {
    id: 'high-risk',
    title: 'High Risk',
    icon: 'AlertTriangle',
    color: '#ed8a09',
    suffix: ' Require attention',
  },
  {
    id: 'growing',
    title: 'Growing',
    icon: 'TrendingUp',
    color: '#ed8a09',
    suffix: ' Positive Trend',
  },
  {
    id: 'total-value',
    title: 'Total Value',
    icon: 'DollarSign',
    color: '#ed8a09',
    suffix: ' Portfolio',
  },
] as const;

// Mock data for development and testing
export const MOCK_ACCOUNTS: AccountData[] = [
  {
    accountId: 'ACC-001',
    name: 'Los Angeles County Metropolitan Transportation Authority (Metro)',
    clientMarketSector: 'Transportation',
    location: 'Los Angeles, CA',
    internalContact: 'David Rodriguez',
    hostingArea: 'West Coast Office',
    clientType: 'Tire 1' as const,
    msaInPlace: true,
    totalOpportunities: 8,
    totalValue: '$8.5M',
    lastContact: '2024-01-15',
    aiHealthScore: 92,
    healthTrend: 'up' as const,
    riskLevel: 'low' as const,
    revenueGrowth: 15.3,
    communicationFrequency: 8,
    winRate: 87,
  },
  {
    accountId: 'ACC-002',
    name: 'San Francisco Municipal Transportation Agency (SFMTA)',
    clientMarketSector: 'Transportation',
    location: 'San Francisco, CA',
    internalContact: 'Sarah Chen',
    hostingArea: 'West Coast Office',
    clientType: 'Tire 2' as const,
    msaInPlace: true,
    totalOpportunities: 6,
    totalValue: '$6.2M',
    lastContact: '2024-01-10',
    aiHealthScore: 78,
    healthTrend: 'stable' as const,
    riskLevel: 'medium' as const,
    revenueGrowth: 8.7,
    communicationFrequency: 6,
    winRate: 72,
  },
  {
    accountId: 'ACC-003',
    name: 'Chicago Transit Authority (CTA)',
    clientMarketSector: 'Transportation',
    location: 'Chicago, IL',
    internalContact: 'Michael Johnson',
    hostingArea: 'Central Office',
    clientType: 'Tire 3' as const,
    msaInPlace: false,
    totalOpportunities: 4,
    totalValue: '$3.8M',
    lastContact: '2024-01-05',
    aiHealthScore: 65,
    healthTrend: 'down' as const,
    riskLevel: 'high' as const,
    revenueGrowth: -2.1,
    communicationFrequency: 3,
    winRate: 58,
  },
];
