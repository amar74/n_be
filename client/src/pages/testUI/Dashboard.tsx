import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import AccountsContent from './AccountsContent';

const Dashboard: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ backgroundColor: '#F5F3F2' }}>
      {/* Fixed Header */}
      <Header onMenuClick={() => setSidebarOpen(true)} />
      
      {/* Main layout below header */}
      <div className="flex flex-1 min-h-0">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 overflow-y-auto overflow-x-hidden">
          <AccountsContent />
        </main>
      </div>
    </div>
  );
};

export default Dashboard;