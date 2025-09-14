import { memo } from 'react';
import { AccountsHeader } from './components/AccountsHeader';
import { AccountsStats } from './components/AccountsStats';
import { AccountsList } from './components/AccountsList';
import { useAccountsPage } from './useAccountsPage';

function AccountsPage() {
  const {
    accounts,
    stats,
    isLoading,
    handleCreateAccount,
    handleAccountClick,
    handleExport,
    handleStatClick,
  } = useAccountsPage();

  return (
    <div className="w-full h-full font-['Inter',_system-ui,_-apple-system,_sans-serif]">
      <div className="flex flex-col gap-7 w-full p-6">
        {/* Header Section */}
        <div>
          <AccountsHeader 
            onCreateAccount={handleCreateAccount}
            onExport={handleExport}
          />
        </div>

        {/* Stats Cards Section */}
        <div>
          <AccountsStats 
            stats={stats}
            onStatClick={handleStatClick}
          />
        </div>

        {/* Accounts List Section */}
        <div className="pt-[48px]">
          <AccountsList 
            accounts={accounts}
            isLoading={isLoading}
            onAccountClick={handleAccountClick}
          />
        </div>
      </div>
    </div>
  );
}

export default memo(AccountsPage);
