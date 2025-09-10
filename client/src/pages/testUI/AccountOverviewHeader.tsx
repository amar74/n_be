import React from 'react';
import { useState } from "react";
const AccountOverviewHeader: React.FC = () => {
    const [isEditing, setIsEditing] = useState(false);
    const handleEditClick = () => {
    setIsEditing((prev) => !prev); // toggle edit state
  };
  return (
    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-3">
      <div>
        <h1 className=" text-xl sm:text-3xl font-semibold text-orange-400 mb-0.5">Los Angeles County Metropolitan Transportation Authority (Metro)</h1>
        <p className="text-xs sm:font-semibold text-gray-500">ACC-001</p>
      </div>
      
      <div className="flex items-center space-x-4 mt-4 lg:mt-0">
        <button onClick={handleEditClick} className={`${isEditing ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'} flex items-center space-x-2 px-4 py-2 border-[1px] border-gray-400 rounded-xl transition-colors`}>
          <span className="text-sm font-medium " >Edit Account</span>
        </button>   
      </div>
    </div>
  );
};

export default AccountOverviewHeader;