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
