import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header2 from './Header2';
import Breadcrumb from './Breadcrumb';
import OverviewMetrics from './OverviewMetrics';
import AccountOverviewHeader from './AccountOverviewHeader';
import AccountOverviewMenu from './AccountOverviewMenu';
import AccountInformationEdit from './AccountInformationEdit';
import RecentActivity from './RecentActivity';

const AccountOverviewEdit: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#F5F3F2' }}>
      {/* Fixed Header */}
      <Header2  />
      
      {/* Main layout below header */}
      <div className="flex flex-1 min-h-0">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 overflow-y-auto overflow-x-hidden">
          <div className="flex-1 px-6" style={{ backgroundColor: '#F5F3F2' }}>
      <div className="max-w-none h-full flex flex-col">
        <Breadcrumb />
        <div className="flex-1 flex flex-col min-h-0">
          <AccountOverviewHeader /> 
          <AccountOverviewMenu />
          {/* Menu Tabs (full width) */}
                <div >
                  <OverviewMetrics />
                </div>
                {/* Account Info + Recent Activity */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                  <div className="lg:col-span-2">
                    <AccountInformationEdit />
                  </div>
                  <div>
                    <RecentActivity />
                  </div>
                </div>
        </div>
      </div>
    </div>
        </main>
      </div>
    </div>
  );
};

export default AccountOverviewEdit;