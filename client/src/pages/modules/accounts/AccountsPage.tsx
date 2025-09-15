import { memo } from 'react';
import { AccountsHeader } from './components/AccountsHeader';
import { AccountsStats } from './components/AccountsStats';
import { AccountsList } from './components/AccountsList';
import { CreateAccountModal } from './components/CreateAccountModal';
import { useAccountsPage } from './useAccountsPage';
import { ClientType } from '@/types/accounts';

function AccountsPage() {
  const {
    accounts,
    stats,
    isLoading,
    isCreateModalOpen,
    handleCreateAccount,
    handleCreateAccountSubmit,
    handleAccountClick,
    handleExport,
    handleStatClick,
    setIsCreateModalOpen,
    isCreating,
    handleTierChange
  } = useAccountsPage();

  return (
    <div className="w-full h-full font-['Inter',_system-ui,_-apple-system,_sans-serif]">
      <div className="flex flex-col gap-7 w-full p-6">
        {/* Header Section */}
        <div>
          <AccountsHeader 
            onCreateAccount={handleCreateAccount}
            onExport={handleExport}
            onFilterChange={handleTierChange}
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

      {/* Create Account Modal */}
      <CreateAccountModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateAccountSubmit}
        isLoading={isCreating}
      />
    </div>
  );
}

export default memo(AccountsPage);
