import React from 'react';
import { Sparkle,Cpu,MapPin,TrendUp,User,Buildings } from 'phosphor-react';

interface Account {
  id: number;
  name: string;
  score: string;
  riskLevel: string;
  riskColor: string;
  riskBg: string;
  location: string;
  office: string;
  tier: string;
  category: string;
  value: string;
  valueColor: string;
  growth: string;
  growthColor: string;
  growthBg: string;
  borderColor: string;
  accName:string;
}

interface AccountCardProps {
  account: Account;
}

// Helper function to get border color based on risk level
const getBorderColor = (riskLevel: string): string => {
  switch (riskLevel.toLowerCase()) {
    case 'low risk':
      return '#10B981'; // green
    case 'medium risk':
      return '#F59E0B'; // orange
    case 'high risk':
      return '#EF4444'; // red
    default:
      return '#6B7280'; // gray
  }
};

const AccountCard: React.FC<AccountCardProps> = ({ account }) => {
  return (
    <div 
      className="bg-white rounded-2xl p-4 hover:shadow-lg transition-all duration-200 cursor-pointer relative overflow-hidden border-b-4"
      style={{ borderBottomColor: getBorderColor(account.riskLevel) }}
    >
      {/* Header with title and star */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg xl:text-lg font-bold text-gray-900 leading-tight pr-6">
          {account.name}
        </h3>
        <div className="flex-shrink-0 w-10 h-10 mt-1 bg-gray-100 rounded-full flex items-center justify-center">
          <Sparkle className="text-orange-400" weight='fill' size={18} />
        </div>
      </div>

      {/* Score and Risk badges */}
        <div className="flex items-center space-x-2 mb-2">
        <div
          className={`flex items-center space-x-2 px-2 py-0.5 rounded-full border ${account.borderColor} ${account.growthBg}`}
        >
          <div className="w-4 h-4 bg-[#7758FF] rounded-sm flex items-center justify-center">
            <Cpu className="text-white" size={10} />
          </div>
          <span className={`text-sm font-semibold  ${account.growthColor}`}>
            {account.score}
          </span>
          <TrendUp className={account.growthColor} size={12} />
        </div>
        <div
          className={`px-3 items-center rounded-full border ${account.borderColor} ${account.riskBg}`}
        >
          <span className={`text-sm font-medium  ${account.riskColor}`}>
            {account.riskLevel}
          </span>
        </div>
      </div>

      {/* Contact and location info */}
      <div className="flex items-center space-x-1 mb-3 text-gray-400 text-xs">
        <div className="flex items-center space-x-0 border-r border-gray-200 pr-2">
          <User size={16} className="text-gray-400" />
          <span className="truncate">{account.accName}</span>
        </div>
        <div className="flex items-center space-x-1.5 border-r border-gray-200 pr-2">
          <MapPin size={16} className="text-gray-400" />
          <span className="truncate">{account.location}</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <Buildings size={16} className="text-gray-400" />
          <span className="truncate">{account.office}</span>
        </div>
      </div>

      {/* Tier and category */}
      <div className="flex items-center space-x-3 mb-3">
        <span className={`font-semibold text-sm ${account.growthColor}`}>{account.tier}</span>
        <span className="text-gray-300">|</span>
        <span className="text-gray-900 font-semibold text-sm">{account.category}</span>
      </div>

      {/* Divider */}
      <div className="border-t border-gray-200 mb-2"></div>

      {/* Value and growth section */}
      <div className="flex items-end justify-between">
        <div>
          <div className={`text-xl xl:text-xl font-bold mb-1 ${account.valueColor}`}>
            {account.value}
          </div>
          <div className="text-sm font-semibold text-gray-900">Total Value</div>
        </div>
        <div className={`px-1 mb-6  rounded-full border ${account.borderColor} ${account.growthBg}`}>
          <span className={`text-sm font-semibold mx-2 ${account.growthColor}`}>{account.growth}</span>
        </div>
      </div>
    </div>
  );
};

export default AccountCard;