import { User, MapPin, Buildings, Sparkle, Cpu, TrendUp } from 'phosphor-react';
import { AccountListItem } from '@/types/accounts';

interface AccountCardProps {
  account: AccountListItem;
  onClick?: (accountId: string) => void;
}

const getRiskColors = (riskLevel?: string) => {
  switch (riskLevel) {
    case 'low':
      return {
        bg: 'bg-[rgba(95,147,111,0.1)]',
        border: 'border-[#5f936f]',
        text: 'text-[#5f936f]',
        bottomBorder: '#559072',
      };
    case 'medium':
      return {
        bg: 'bg-[rgba(205,129,42,0.1)]',
        border: 'border-[#cd812a]',
        text: 'text-[#cd812a]',
        bottomBorder: '#cd812a',
      };
    case 'high':
      return {
        bg: 'bg-[rgba(255,123,123,0.1)]',
        border: 'border-[#ff7b7b]',
        text: 'text-[#ff7b7b]',
        bottomBorder: '#ff7b7b',
      };
    default:
      return {
        bg: 'bg-[rgba(95,147,111,0.1)]',
        border: 'border-[#5f936f]',
        text: 'text-[#5f936f]',
        bottomBorder: '#559072',
      };
  }
};

export function AccountCard({ account, onClick }: AccountCardProps) {
  // Default to low risk colors since risk level is not in the API
  const colors = getRiskColors('low');
  
  return (
    <div 
      className="bg-white relative rounded-[28px] cursor-pointer hover:shadow-lg transition-shadow w-full min-w-0 h-full flex flex-col"
      onClick={() => onClick?.(account.account_id)}
    >
      <div className="flex flex-col p-5 w-full flex-1">
        {/* Top Content - Flexible */}
        <div className="flex flex-col gap-5 w-full flex-1">
          {/* Header Section */}
          <div className="flex flex-col gap-4 w-full">
            {/* Title and Action Button */}
            <div className="flex items-center justify-between w-full">
              <div className="flex-1 min-w-0 pr-3">
                <h3 className="font-['Inter:Bold',_sans-serif] font-bold text-[#0f0901] text-[16px] leading-6 line-clamp-2">
                  {account.client_name}
                </h3>
              </div>
              <div className="bg-[#f3f3f3] flex items-center justify-center p-3 rounded-[28px] size-14 flex-shrink-0">
                <div aria-hidden="true" className="absolute border border-[#e6e6e6] border-solid inset-0 pointer-events-none rounded-[28px]" />
                  <Sparkle className="text-orange-400" size={24} weight='fill'/>
              </div>
            </div>

            {/* Health Score and Risk Badges */}
            <div className="flex flex-wrap gap-3 items-center w-full">
              {/* Health Score Badge */}
              <div className={`${colors.bg} flex gap-2 items-center px-3 py-1 rounded-full border-[1px] border-[#5f936f] relative`}>
                <div aria-hidden="true" className={`absolute ${colors.border} border-solid inset-0 pointer-events-none rounded-full`} />
                <div className="size-[18px]">
                  {/* Health icon placeholder */}
                  <Cpu size={18} weight="fill" className="text-purple-500" />
                </div>
                <span className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold ${colors.text} text-[14px] whitespace-nowrap`}>
                  {account.ai_health_score || 92}%
                </span>
                <div className="size-[18px]">
                  <TrendUp size={18} className="text-[#5f936f]" />       
                </div>
              </div>

              {/* Risk Level Badge */}
              <div className={`${colors.bg} flex gap-2 items-center px-3 py-1 border-[1px] border-[#5f936f] rounded-full relative`}>
                <div aria-hidden="true" className={`absolute ${colors.border} border-solid inset-0 pointer-events-none rounded-full`} />
                <span className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold ${colors.text} text-[14px] whitespace-nowrap capitalize`}>
                  Low risk
                </span>
              </div>
            </div>
            {/* Health Score Badge */}
            {account.ai_health_score !== null && (
              <div className="flex flex-wrap gap-3 items-center w-full">
                <div className={`${colors.bg} flex gap-2 items-center px-3 py-1 rounded-full relative`}>
                  <div aria-hidden="true" className={`absolute ${colors.border} border-solid inset-0 pointer-events-none rounded-full`} />
                  <div className="size-[18px]">
                    {/* Health icon placeholder */}
                  </div>
                  <span className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold ${colors.text} text-[14px] whitespace-nowrap`}>
                    {account.ai_health_score}%
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Contact Info Section */}
          <div className="flex flex-wrap items-center gap-3 w-full">
            {account.primary_contact_name && (
              <>
                <div className="flex gap-2 items-center min-w-0">
                  <User className="size-5 text-gray-400 flex-shrink-0" />
                  <span className="font-['Inter:Medium',_sans-serif] font-medium text-[14px] text-gray-400 truncate">
                    {account.primary_contact_name}
                  </span>
                </div>
                <div className="bg-gray-400 h-3.5 w-px hidden sm:block" />
              </>
            )}
            {account.client_address?.line1 && (
              <>
                <div className="flex gap-2 items-center min-w-0">
                  <MapPin className="size-5 text-gray-400 flex-shrink-0" />
                  <span className="font-['Inter:Medium',_sans-serif] font-medium text-[14px] text-gray-400 truncate">
                    {account.client_address.line1}
                  </span>
                </div>
                <div className="bg-gray-400 h-3.5 w-px hidden sm:block" />
              </>
            )}

            <div className="flex gap-2 items-center min-w-0">
              <Buildings className="size-5 text-gray-400 flex-shrink-0" />
              <span className="font-['Inter:Medium',_sans-serif] font-medium text-[14px] text-gray-400 truncate">
                {/* TODO: get this data from account */}
                West Coast Office
              </span>
            </div>
          </div>

          {/* Tier and Sector */}
          <div className="flex flex-wrap gap-3 items-center w-full">
            <span className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold ${colors.text} text-[16px] whitespace-nowrap capitalize`}>
              {account.client_type.replace('_', ' ')}
            </span>
            {account.market_sector && (
              <>
                <div className="bg-gray-400 h-3.5 w-px hidden sm:block" />
                <span className="font-['Inter:Medium',_sans-serif] font-medium text-[#0f0901] text-[16px] whitespace-nowrap">
                  {account.market_sector}
                </span>
              </>
            )}
          </div>
        </div>

        {/* Bottom Content - Fixed Position */}
        <div className="flex flex-col gap-5 w-full mt-auto">
          {/* Divider Line */}
          <div className="w-full border-t border-gray-200" />

          {/* Total Value Section */}
          <div className="flex flex-col gap-2 w-full">
            <div className="flex items-center justify-between w-full">
              <span className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold ${colors.text} text-[28px] whitespace-nowrap`}>
                ${account.total_value?.toLocaleString() || '0'}
              </span>
              <div className={`${colors.bg} flex gap-2 items-center px-3 py-1 rounded-full relative`}>
                <div aria-hidden="true" className={`absolute ${colors.border} border-solid inset-0 pointer-events-none rounded-full`} />
                <span className={`font-['Inter:Semi_Bold',_sans-serif} font-semibold ${colors.text} text-[14px] whitespace-nowrap`}>
                  +15.3% Growth
                </span>
              </div>
            </div>
            <div className="w-full">
              <span className="font-['Inter:Medium',_sans-serif] font-medium text-[#0f0901] text-[18px]">
                Total Value
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Colored Border */}
      <div 
        aria-hidden="true" 
        className="absolute border-[0px_0px_4px] border-solid bottom-[-4px] left-0 pointer-events-none right-0 rounded-[28px] top-0"
        style={{ borderBottomColor: colors.bottomBorder }}
      />
    </div>
  );
}
