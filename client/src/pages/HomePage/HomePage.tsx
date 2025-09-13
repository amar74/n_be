import { Outlet } from 'react-router-dom';
import { DashboardSidebar } from '@/components/DashboardSidebar';
import { useHomePage } from './useHomePage';
import { memo } from 'react';

function HomePage() {
  const {
    user,
    isAuthLoading,
    isAuthenticated,
  } = useHomePage();

  // Show loading during auth initialization to prevent flicker
  if (isAuthLoading) {
    return (
      <div className="min-h-screen bg-[#F9FAFB] flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Redirect if not authenticated (shouldn't happen, but safety check)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#F9FAFB] flex items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen  bg-[#F9FAFB] flex font-['Inter',_'Poppins',_system-ui,_-apple-system,_sans-serif]">
      {/* Sidebar */}
      <DashboardSidebar />
      
      {/* Main Content Area */}
      <div className="ml-[260px] min-h-screen">
        {/* Welcome Section - Only shown on root dashboard */}
        <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
          <div className="mb-12">
            <h2 className="text-3xl font-semibold text-[#111827] mb-4 leading-tight">
              Welcome to Your Dashboard
            </h2>
            <p className="text-base text-[#1F2937] leading-relaxed">
              Manage your clients, pursuits, proposals, and track your success metrics
            </p>
          </div>
          
          {/* Content will be rendered here via Outlet */}
          <Outlet />
        </div>
      </div>
    </div>
  );
}

export default memo(HomePage);
