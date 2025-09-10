import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header2 from './Header2';
import Breadcrumb from './Breadcrumb';
import OverviewMetrics from './OverviewMetrics';
import AccountOverviewHeader from './AccountOverviewHeader';
import AccountOverviewMenu from './AccountOverviewMenu';
import { AccountNotesAndDocuments } from './AccountNotesAndDocuments';


const MyAccountNotes: React.FC = () => {
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
          <OverviewMetrics />
          <AccountOverviewMenu /> 
          {/* Account Notes and account documents design  */}
          <AccountNotesAndDocuments/>

        </div>
      </div>
    </div>
        </main>
      </div>
    </div>
  );
};

export default MyAccountNotes;