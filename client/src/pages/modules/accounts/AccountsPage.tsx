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
    <div className="bg-[#f5f3f2] min-h-screen font-['Inter',_system-ui,_-apple-system,_sans-serif]">
      {/* Main Content Area - accounting for sidebar */}
      <div className="ml-0 min-h-screen">
        <div className="flex flex-col gap-7 left-0 top-0 w-full px-0 py-0">
          {/* Header Section */}
          <div className="px-0 pt-0 pb-0">
            <AccountsHeader 
              onCreateAccount={handleCreateAccount}
              onExport={handleExport}
            />
          </div>

          {/* Stats Cards Section */}
          <div className="px-0">
            <AccountsStats 
              stats={stats}
              onStatClick={handleStatClick}
            />
          </div>

          {/* Accounts List Section */}
          <div className="px-0 pt-[48px]">
            <AccountsList 
              accounts={accounts}
              isLoading={isLoading}
              onAccountClick={handleAccountClick}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(AccountsPage);
