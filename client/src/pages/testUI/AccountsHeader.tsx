import React from 'react';
import { CaretDown, Files,Users} from 'phosphor-react'
import CreateAccountModal from './CreateAccountModal';
const AccountsHeader: React.FC = () => {
  return (
    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-5">
      <div>
        <h1 className="text-3xl font-semibold text-orange-400 mb-0.5">My Accounts</h1>
        <p className="text-md text-gray-500">Manage client accounts and relationship data</p>
      </div>
      
      <div className="flex items-center space-x-4 mt-4 lg:mt-0">
        <button className="flex items-center space-x-2 px-4 py-2 bg-white border-[1px] border-gray-400 rounded-full hover:bg-gray-50 transition-colors">
          <Users size={16} weight='fill' className="text-gray-900" />
          <span className="text-sm font-medium text-gray-700">All Accounts</span>
          <CaretDown size={16} className="text-gray-500" />
        </button>
        
        <button className="flex items-center space-x-2 px-4 py-2 bg-white border-[1px] border-gray-400 rounded-full hover:bg-gray-50 transition-colors">
          <span className="text-sm font-medium text-gray-700">Actions</span>
          <CaretDown size={16} className="text-gray-500" />
        </button>
        
        <button className="flex items-center space-x-2 px-4 py-2 bg-gray-50 border-[1px] border-gray-300 rounded-full hover:bg-gray-100 transition-colors">
          <Files size={16} weight='fill' className="text-gray-900" />
          <span className="text-sm font-medium text-gray-700">Client Survey</span>
        </button>
        
        {/* <button className="flex items-center space-x-2 px-4 py-2 bg-gray-900 text-white rounded-full hover:bg-gray-800 transition-colors">
          <Plus size={16} />
          <span className="text-sm font-medium">Create Account</span>
        </button> */}
        <CreateAccountModal />
      </div>
    </div>
  );
};

export default AccountsHeader;