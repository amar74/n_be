import { memo } from 'react';
import { TabNavigation } from './components/TabNavigation';
import { AccountStatsCards } from './components/AccountStatsCards';
import { AccountInformationForm } from './components/AccountInformationForm';
import { RecentActivity } from './components/RecentActivity';
import { NotesTab } from './notes';
import { useAccountDetailsPage } from './useAccountDetailsPage';

function AccountDetailsPage() {
  const {
    account,
    isLoading,
    error,
    activeTab,
    isEditing,
    formData,
    statsCards,
    recentActivity,
    handleTabChange,
    handleEditToggle,
    handleFormChange,
    handleSaveChanges,
    handleBackToAccounts,
    isUpdating,
  } = useAccountDetailsPage();

  // Loading state
  if (isLoading || (!account && !error)) {
    return (
      <div className="w-full h-full bg-[#f5f3f2] font-inter flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ed8a09]"></div>
          <p className="text-[#6e6e6e] text-sm">Loading account details...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !isLoading) {
    return (
      <div className="w-full h-full bg-[#f5f3f2] font-inter flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4 text-center">
          <div className="text-red-500 text-6xl">⚠️</div>
          <h3 className="text-lg font-medium text-[#0f0901]">Account Not Found</h3>
          <p className="text-[#6e6e6e] mb-4">
            The account you're looking for doesn't exist or you don't have permission to view it.
          </p>
          <button
            onClick={handleBackToAccounts}
            className="bg-[#0f0901] text-white px-6 py-2 rounded-[16px] font-medium"
          >
            Return to Accounts
          </button>
        </div>
      </div>
    );
  }

  if (!account || !formData) {
    return (
      <div className="w-full h-full bg-[#f5f3f2] font-inter flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ed8a09]"></div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-[#f5f3f2] font-inter">
      <div className="flex flex-col gap-7 w-full px-7 pt-2 pb-4">
        {/* Header Section */}
        <div className="flex flex-col gap-2 items-center justify-start w-full">
          {/* Title and Edit Button */}
          <div className="flex flex-col h-[85px] items-start justify-between w-full">
            <div className="flex items-end justify-between w-full">
              <div className="flex flex-col gap-2 items-start justify-start w-[1120px]">
                <h1 
                  className="font-inter font-medium text-[#ed8a09] text-[40px] text-center leading-normal overflow-hidden text-ellipsis whitespace-nowrap"
                  style={{ width: 'min-content', maxWidth: '100%' }}
                >
                  {account.client_name}
                </h1>
                <p className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
                  {account.account_id}
                </p>
              </div>
              <button
                onClick={handleEditToggle}
                className="bg-[#0f0901] border border-[#0f0901] rounded-[16px] h-14 flex items-center justify-center px-6 py-2 w-[148px]"
              >
                <span className="font-inter font-medium text-white text-[14px] leading-[24px]">
                  {isEditing ? 'Cancel Edit' : 'Edit Account'}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />

        {/* Stats Cards */}
        <AccountStatsCards stats={statsCards} />

        {/* Main Content */}
        <div className={`w-full ${activeTab === 'overview' ? 'flex gap-7 items-start justify-start' : ''}`}>
          {/* Tab Content */}
          <div className={activeTab === 'overview' ? 'flex-1' : 'w-full'}>
            {activeTab === 'overview' && (
              <AccountInformationForm
                formData={formData}
                accountId={account.account_id}
                isEditing={isEditing}
                isUpdating={isUpdating}
                onFormChange={handleFormChange}
                onSave={handleSaveChanges}
                onCancel={handleEditToggle}
              />
            )}
            
            {activeTab === 'notes' && (
              <NotesTab accountId={account.account_id} />
            )}
            
            {/* Placeholder for other tabs */}
            {!['overview', 'notes'].includes(activeTab) && (
              <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <h3 className="font-inter font-semibold text-[#0f0901] text-[18px] mb-2">
                    {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Tab
                  </h3>
                  <p className="font-inter font-medium text-[#a7a7a7] text-[16px]">
                    This tab is coming soon. Stay tuned for updates!
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Recent Activity Sidebar - Only show on Overview tab */}
          {activeTab === 'overview' && (
            <RecentActivity activities={recentActivity} />
          )}
        </div>
      </div>
    </div>
  );
}

export default memo(AccountDetailsPage);
