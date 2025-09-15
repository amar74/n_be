import { ClientType } from '@/types/accounts';

export interface AccountData {
  accountId: string;
  name: string;
  clientMarketSector: string;
  location: string;
  internalContact: string;
  hostingArea: string;
  clientType: 'Tire 1' | 'Tire 2' | 'Tire 3';
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

export interface AccountsPageProps {
  // Add any props if needed
}

export interface AccountStatsData {
  totalAccounts: number;
  aiHealthScore: number;
  highRiskCount: number;
  growingCount: number;
  totalValue: string;
}

export interface FilterState {
  search: string;
  tier: 'all' | ClientType;
}

// Re-export from the modal component
export type { CreateAccountModalProps } from './components/CreateAccountModal/CreateAccountModal.types';
