import React from 'react';
import Breadcrumb from './Breadcrumb';
import MetricsCards from './MetricsCards';
import AccountsHeader from './AccountsHeader';
import AccountsList from './AccountsList';

const AccountsContent: React.FC = () => {
  return (
    <div className="flex-1 px-6" style={{ backgroundColor: '#F5F3F2' }}>
      <div className="max-w-none h-full flex flex-col">
        <Breadcrumb />
        <div className="flex-1 flex flex-col min-h-0">
          <AccountsHeader />
          <MetricsCards />
          <AccountsList />
        </div>
      </div>
    </div>
  );
};

export default AccountsContent;