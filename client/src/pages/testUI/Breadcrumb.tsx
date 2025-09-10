import React from 'react';
import { CaretRight } from 'phosphor-react';

const Breadcrumb: React.FC = () => {
  return (
    <nav className="flex items-center space-x-2 text-sm mb-2">
      <span className="text-gray-500 font-medium">Dashboard</span>
      <CaretRight size={14} className="text-gray-400" />
      <span className="text-gray-500 font-medium">Accounts</span>
    </nav>
  );
};

export default Breadcrumb;