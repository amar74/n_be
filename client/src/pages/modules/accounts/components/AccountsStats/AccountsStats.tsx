import { Building, Brain, AlertTriangle, TrendingUp, DollarSign } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { AccountStatsData } from '../../AccountsPage.types';

interface AccountsStatsProps {
  stats: AccountStatsData;
  onStatClick?: (statId: string) => void;
}

const STAT_CONFIGS = [
  {
    id: 'total-accounts',
    title: 'Total Accounts',
    icon: Building,
    getValue: (stats: AccountStatsData) => stats.totalAccounts.toString(),
    suffix: '',
  },
  {
    id: 'ai-health-score',
    title: 'AI Health Score',
    icon: Brain,
    getValue: (stats: AccountStatsData) => `${stats.aiHealthScore}%`,
    suffix: 'Average',
  },
  {
    id: 'high-risk',
    title: 'High Risk',
    icon: AlertTriangle,
    getValue: (stats: AccountStatsData) => stats.highRiskCount.toString(),
    suffix: 'Require attention',
  },
  {
    id: 'growing',
    title: 'Growing',
    icon: TrendingUp,
    getValue: (stats: AccountStatsData) => stats.growingCount.toString(),
    suffix: 'Positive Trend',
  },
  {
    id: 'total-value',
    title: 'Total Value',
    icon: DollarSign,
    getValue: (stats: AccountStatsData) => stats.totalValue,
    suffix: 'Portfolio',
  },
];

export function AccountsStats({ stats, onStatClick }: AccountsStatsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 w-full">
      {STAT_CONFIGS.map((config) => {
        const Icon = config.icon;
        const value = config.getValue(stats);
        
        return (
          <div
            key={config.id}
            className="bg-neutral-50 h-[97px] relative rounded-[20px] cursor-pointer hover:shadow-md transition-shadow min-w-0"
            onClick={() => onStatClick?.(config.id)}
          >
            <div className="h-[97px] overflow-clip relative w-full flex items-center p-4">
              {/* Icon Section */}
              <div className="bg-[#f3f3f3] flex items-center justify-center p-3 rounded-full size-14 flex-shrink-0">
                <Icon className="size-7 text-orange-500" />
              </div>
              
              {/* Text Section */}
              <div className="ml-4 flex-1 min-w-0">
                <div className="font-['Inter:Medium',_sans-serif] font-medium text-[#a7a7a7] text-sm tracking-[-0.28px] truncate">
                  {config.title}
                </div>
                <div className="font-['Inter:Semi_Bold',_sans-serif] font-semibold text-black text-xl leading-tight">
                  <span className="font-semibold">
                    {value}
                  </span>
                  {config.suffix && (
                    <span className="font-medium text-[#0f0901] text-sm ml-1">
                      {config.suffix}
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            {/* Border */}
            <div aria-hidden="true" className="absolute border border-[#6c6c6c] border-solid inset-0 pointer-events-none rounded-[20px]" />
          </div>
        );
      })}
    </div>
  );
}
