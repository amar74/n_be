import { DollarSign, Target, Calendar, Award } from 'lucide-react';
import { AccountStatsCard } from '../../../AccountDetailsPage.types';

const iconMap = {
  DollarSign,
  Target,
  Calendar,
  Award,
};

interface AccountStatsCardsProps {
  stats: AccountStatsCard[];
}

export function AccountStatsCards({ stats }: AccountStatsCardsProps) {
  return (
    <div className="flex gap-5 h-[97px] w-full">
      {stats.map((stat) => {
        const IconComponent = iconMap[stat.icon as keyof typeof iconMap];
        
        return (
          <div
            key={stat.id}
            className="flex-1 bg-neutral-50 h-[97px] rounded-[20px] border border-[#6c6c6c] relative overflow-hidden"
          >
            <div className="h-[97px] w-full relative">
              {/* Icon */}
              <div className="absolute left-[17px] top-5">
                <div className="bg-[#f3f3f3] flex items-center justify-center p-3 rounded-[28px] size-14">
                  <IconComponent className="h-7 w-7 text-[#6c6c6c]" />
                </div>
              </div>
              
              {/* Text Content */}
              <div className="absolute left-[91.21px] top-5">
                <div className="font-inter font-medium text-[#a7a7a7] text-[14px] tracking-[-0.28px] leading-[24px]">
                  {stat.title}
                </div>
                <div className="font-inter font-semibold text-black text-[24px] leading-[32px] mt-[1px]">
                  {stat.value}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
