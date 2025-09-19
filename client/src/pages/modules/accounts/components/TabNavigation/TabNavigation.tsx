import React from 'react';
import { 
  LayoutDashboard, 
  Users, 
  UserCheck, 
  Target, 
  Star, 
  BarChart3, 
  FileText, 
  DollarSign 
} from 'lucide-react';
import { TabType } from '../../AccountDetailsPage.types';
import { ACCOUNT_DETAILS_TABS } from '../../AccountDetailsPage.constants';

const iconMap = {
  LayoutDashboard,
  Users,
  UserCheck,
  Target,
  Star,
  BarChart3,
  FileText,
  DollarSign,
};

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="h-20 p-4 border-2 border-[#8c8c8c] rounded-[12px] overflow-hidden">
      <div className="flex gap-5 h-full items-center justify-start overflow-x-auto scrollbar-hide">
        {ACCOUNT_DETAILS_TABS.map((tab) => {
          const IconComponent = iconMap[tab.icon as keyof typeof iconMap];
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                flex-shrink-0 h-full flex items-center justify-center gap-3 px-8 py-5 rounded-[12px] transition-all min-w-fit
                ${isActive 
                  ? 'bg-[#0f0901] text-white border border-[#e4e4e4]' 
                  : 'bg-[#f3f3f3] text-[#0f0901] border border-[#e6e6e6] hover:bg-[#e8e8e8]'
                }
              `}
            >
              <IconComponent className="h-5 w-5" />
              <span className="font-inter font-medium text-[16px] whitespace-nowrap">
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
