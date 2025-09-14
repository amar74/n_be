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
    <div className="content-stretch flex items-start justify-between relative w-full h-[97px] overflow-clip gap-[25.75px]">
      {STAT_CONFIGS.map((config) => {
        const Icon = config.icon;
        const value = config.getValue(stats);
        
        return (
          <div
            key={config.id}
            className="bg-neutral-50 h-[97px] relative rounded-[20px] shrink-0 w-[301px] cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => onStatClick?.(config.id)}
          >
            <div className="h-[97px] overflow-clip relative w-[301px]">
              {/* Text Section */}
              <div className="absolute contents leading-[0] left-[91.21px] not-italic top-5">
                <div className="absolute font-['Inter:Medium',_sans-serif] font-medium h-[22.579px] left-[91.21px] text-[#a7a7a7] text-[14px] top-5 tracking-[-0.28px] w-[116.998px]">
                  <p className="leading-[24px]">{config.title}</p>
                </div>
                <div className="absolute font-['Inter:Semi_Bold',_sans-serif] font-semibold h-[31px] left-[91.21px] text-[24px] text-black top-[43px] w-36">
                  <p className="leading-[32px] not-italic whitespace-pre">
                    <span className="font-['Inter:Semi_Bold',_sans-serif] font-semibold text-[24px]">
                      {value}
                    </span>
                    {config.suffix && (
                      <span className="font-['Inter:Medium',_sans-serif] font-medium text-[#0f0901] text-[16px]">
                        {` ${config.suffix}`}
                      </span>
                    )}
                  </p>
                </div>
              </div>
              
              {/* Icon Section */}
              <div className="absolute contents left-[17px] top-5">
                <div className="absolute bg-[#f3f3f3] box-border content-stretch flex gap-2 items-center justify-center left-[17px] p-[12px] rounded-[28px] size-14 top-5">
                  <Icon className="relative shrink-0 size-7 text-gray-600" />
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
