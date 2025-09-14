import { AccountCard } from '../AccountCard';
import { AccountData } from '../../AccountsPage.types';

interface AccountsListProps {
  accounts: AccountData[];
  isLoading?: boolean;
  onAccountClick?: (accountId: string) => void;
}

export function AccountsList({ accounts, isLoading, onAccountClick }: AccountsListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ed8a09]"></div>
      </div>
    );
  }

  if (accounts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="text-gray-500 text-lg mb-2">No accounts found</div>
        <div className="text-gray-400 text-sm">Try adjusting your search or filters</div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between w-full">
      {accounts.slice(0, 3).map((account) => (
        <div key={account.accountId} className="w-[527px]">
          <AccountCard 
            account={account} 
            onClick={onAccountClick}
          />
        </div>
      ))}
    </div>
  );
}
