import { memo } from 'react';

function DashboardWelcome() {
  return (
    <div className="w-full  mx-auto px-6 sm:px-8 lg:px-12 py-18">
      {/* Welcome Section */}
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-semibold text-[#ED8A09] mb-4 leading-tight">
          Welcome to Your Dashboard
        </h2>
        <p className="text-base text-[#1F2937] leading-relaxed">
          Manage your clients, pursuits, proposals, and track your success metrics
        </p>
      </div>

      {/* Divider Line */}
      <div className="border-b border-[#E5E7EB] mb-8"></div>
      {/* Welcome Message */}
      <div className="text-center py-2">
        <h3 className="text-xl font-semibold text-[#ED8A09] mb-6">
          Select a module from the sidebar to get started
        </h3>
        <p className="text-[#1F2937] max-w-2xl mx-auto leading-relaxed">
          Use the navigation sidebar on the left to access different modules of your business management system. 
          Each module provides comprehensive tools to manage different aspects of your organization.
        </p>
      </div>
    </div>
  );
}

export default memo(DashboardWelcome);
