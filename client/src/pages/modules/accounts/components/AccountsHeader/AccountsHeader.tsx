import { ChevronDown, Building, FileText, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ClientType } from '../CreateAccountModal/CreateAccountModal.types';

interface AccountsHeaderProps {
  onCreateAccount: () => void;
  onExport: (format: string) => void;
  onFilterChange: (filter: ClientType | 'all') => void;
}

export function AccountsHeader({ onCreateAccount, onExport, onFilterChange, }: AccountsHeaderProps) {
  return (
    <div className="content-stretch flex flex-col gap-7 items-start justify-start relative w-full">
      {/* Header Content */}
      <div className="content-stretch flex flex-col h-[85px] items-start justify-between relative shrink-0 w-full">
        <div className="content-stretch flex items-end justify-between relative shrink-0 w-full">
          {/* Title Section */}
          <div className="content-stretch flex flex-col gap-2 items-start justify-start leading-[0] not-italic relative shrink-0 text-nowrap">
            <div className="font-['Inter:Semi_Bold',_sans-serif] font-semibold relative shrink-0 text-[#ed8a09] text-[40px] text-center">
              <p className="leading-[normal] text-nowrap whitespace-pre">My Accounts</p>
            </div>
            <div className="font-['Inter:Medium',_sans-serif] font-medium relative shrink-0 text-[#a7a7a7] text-[16px]">
              <p className="leading-[normal] text-nowrap whitespace-pre">Manage client accounts and relationship data</p>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-wrap gap-3 items-start justify-start">
            {/* All Accounts Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <div className="bg-white box-border flex h-[46px] items-center justify-between px-5 py-3 relative rounded-[24px] min-w-[180px] cursor-pointer hover:shadow-md transition-shadow">
                  <div aria-hidden="true" className="absolute border border-[#525151] border-solid inset-[-1px] pointer-events-none rounded-[25px]" />
                  <div className="content-stretch flex gap-2 items-center justify-start relative shrink-0">
                    <Building className="relative shrink-0 size-5 text-gray-600" />
                    <div className="font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 text-[#0f0901] text-[14px] text-nowrap">
                      <p className="leading-[normal] whitespace-pre">All Accounts</p>
                    </div>
                  </div>
                  <ChevronDown className="relative shrink-0 size-5 text-gray-600" />
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-white border border-gray-200 shadow-lg">
                <DropdownMenuItem onClick={() => onFilterChange('all')}>All Accounts</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onFilterChange(ClientType.TIER_1)}>Tier 1 Accounts</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onFilterChange(ClientType.TIER_2)}>Tier 2 Accounts</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onFilterChange(ClientType.TIER_3)}>Tier 3 Accounts</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Actions Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <div className="bg-white box-border flex h-[46px] items-center justify-between px-5 py-3 relative rounded-[24px] min-w-[140px] cursor-pointer hover:shadow-md transition-shadow">
                  <div aria-hidden="true" className="absolute border border-[#525151] border-solid inset-[-1px] pointer-events-none rounded-[25px]" />
                  <div className="font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 text-[#0f0901] text-[14px] text-nowrap">
                    <p className="leading-[normal] whitespace-pre">Actions</p>
                  </div>
                  <ChevronDown className="relative shrink-0 size-5 text-gray-600" />
                </div>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-white border border-gray-200 shadow-lg">
                <DropdownMenuItem onClick={() => onExport('excel')}>
                  Export to Excel
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onExport('csv')}>
                  Export to CSV
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Client Survey Button */}
            <div className="bg-[rgba(255,255,255,0)] box-border flex gap-2.5 h-[46px] items-center justify-center px-4 py-2 relative rounded-[100px] min-w-[150px] cursor-pointer hover:shadow-md transition-shadow">
              <div aria-hidden="true" className="absolute border border-black border-solid inset-0 pointer-events-none rounded-[100px]" />
              <FileText className="relative shrink-0 size-6 text-black" />
              <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[14px] text-black text-nowrap">
                <p className="leading-[24px] whitespace-pre">Client Survey</p>
              </div>
            </div>

            {/* Create Account Button */}
            <div 
              onClick={onCreateAccount}
              className="bg-[#0f0901] box-border flex gap-2.5 h-[46px] items-center justify-center px-4 py-2 relative rounded-[100px] min-w-[150px] cursor-pointer hover:shadow-md transition-shadow"
            >
              <Plus className="relative shrink-0 size-6 text-white" />
              <div className="font-['Inter:Medium',_sans-serif] font-medium leading-[0] not-italic relative shrink-0 text-[14px] text-nowrap text-white">
                <p className="leading-[24px] whitespace-pre">Create Account</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
