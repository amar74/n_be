import { User, MapPin, Building } from 'lucide-react';
import { AccountData } from '../../AccountsPage.types';

interface AccountCardProps {
  account: AccountData;
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
  const colors = getRiskColors(account.riskLevel);
  
  return (
    <div className="bg-white relative rounded-[28px] shrink-0 cursor-pointer hover:shadow-lg transition-shadow">
      <div className="box-border content-stretch flex flex-col gap-2 items-start justify-start overflow-clip p-[20px] relative">
        <div className="content-stretch flex flex-col gap-5 items-start justify-start relative shrink-0 w-[487px]">
          {/* Header Section */}
          <div className="content-stretch flex flex-col gap-4 items-start justify-start relative shrink-0 w-[474px]">
            {/* Title and Action Button */}
            <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
              <div className="-webkit-box css-cqbe6b flex-col font-['Inter:Bold',_sans-serif] font-bold h-14 justify-center leading-[0] not-italic overflow-ellipsis overflow-hidden relative shrink-0 text-[#0f0901] text-[16px] w-[390px]">
                <p className="leading-[24px]">{account.name}</p>
              </div>
              <div className="bg-[#f3f3f3] box-border content-stretch flex gap-2 items-center justify-center p-[12px] relative rounded-[28px] shrink-0 size-14">
                <div aria-hidden="true" className="absolute border border-[#e6e6e6] border-solid inset-0 pointer-events-none rounded-[28px]" />
                <div className="relative shrink-0 size-7">
                  {/* Action icon placeholder */}
                </div>
              </div>
            </div>

            {/* Health Score and Risk Badges */}
            <div className="content-stretch flex gap-3 items-center justify-start relative shrink-0 w-full">
              {/* Health Score Badge */}
              <div className={`${colors.bg} box-border content-stretch flex gap-2 items-center justify-center px-3 py-1 relative rounded-[100px] shrink-0`}>
                <div aria-hidden="true" className={`absolute ${colors.border} border-solid inset-0 pointer-events-none rounded-[100px]`} />
                <div className="relative shrink-0 size-[18px]">
                  {/* Health icon placeholder */}
                </div>
                <div className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 ${colors.text} text-[14px] text-nowrap`}>
                  <p className="leading-[normal] whitespace-pre">{account.aiHealthScore || 92}%</p>
                </div>
                <div className="relative shrink-0 size-[18px]">
                  {/* Trend icon placeholder */}
                </div>
              </div>

              {/* Risk Level Badge */}
              <div className={`${colors.bg} box-border content-stretch flex gap-2 items-center justify-center px-3 py-1 relative rounded-[100px] shrink-0`}>
                <div aria-hidden="true" className={`absolute ${colors.border} border-solid inset-0 pointer-events-none rounded-[100px]`} />
                <div className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 ${colors.text} text-[14px] text-nowrap`}>
                  <p className="leading-[normal] whitespace-pre capitalize">{account.riskLevel || 'Low'} risk</p>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Info Section */}
          <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
            <div className="content-stretch flex gap-2 items-center justify-start relative shrink-0">
              <User className="relative shrink-0 size-5 text-[silver]" />
              <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[14px] text-[silver] text-nowrap">
                <p className="leading-[normal] whitespace-pre">{account.internalContact}</p>
              </div>
            </div>
            <div className="bg-[silver] h-3.5 shrink-0 w-px" />
            <div className="content-stretch flex gap-2 items-center justify-start relative shrink-0">
              <MapPin className="relative shrink-0 size-5 text-[silver]" />
              <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[14px] text-[silver] text-nowrap">
                <p className="leading-[normal] whitespace-pre">{account.location}</p>
              </div>
            </div>
            <div className="bg-[silver] h-3.5 shrink-0 w-px" />
            <div className="content-stretch flex gap-2 items-center justify-start relative shrink-0">
              <Building className="relative shrink-0 size-5 text-[silver]" />
              <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[14px] text-[silver] text-nowrap">
                <p className="leading-[normal] whitespace-pre">{account.hostingArea}</p>
              </div>
            </div>
          </div>

          {/* Tier and Sector */}
          <div className="content-stretch flex gap-3 items-center justify-start relative shrink-0">
            <div className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 ${colors.text} text-[16px] text-nowrap`}>
              <p className="leading-[normal] whitespace-pre">{account.clientType}</p>
            </div>
            <div className="bg-[silver] h-3.5 shrink-0 w-px" />
            <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#0f0901] text-[16px] text-nowrap">
              <p className="leading-[normal] whitespace-pre">{account.clientMarketSector}</p>
            </div>
          </div>

          {/* Divider Line */}
          <div className="h-0 relative shrink-0 w-full">
            <div className="absolute bottom-0 left-0 right-0 top-[-1px] border-t border-gray-200" />
          </div>

          {/* Total Value Section */}
          <div className="content-stretch flex flex-col gap-2 items-start justify-start relative shrink-0 w-[486px]">
            <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
              <div className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 ${colors.text} text-[28px] text-nowrap`}>
                <p className="leading-[normal] whitespace-pre">{account.totalValue}</p>
              </div>
              <div className={`${colors.bg} box-border content-stretch flex gap-2 items-center justify-center px-3 py-1 relative rounded-[100px] shrink-0`}>
                <div aria-hidden="true" className={`absolute ${colors.border} border-solid inset-0 pointer-events-none rounded-[100px]`} />
                <div className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 ${colors.text} text-[14px] text-nowrap`}>
                  <p className="leading-[normal] whitespace-pre">+{account.revenueGrowth || 15.3}% Growth</p>
                </div>
              </div>
            </div>
            <div className="content-stretch flex gap-2 items-start justify-start relative shrink-0 w-full">
              <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[#0f0901] text-[18px] text-nowrap">
                <p className="leading-[normal] whitespace-pre">Total Value</p>
              </div>
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
