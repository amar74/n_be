import { Outlet } from 'react-router-dom';
import { DashboardSidebar } from '@/components/DashboardSidebar';
import { useHomePage } from './useHomePage';
import { useBreadcrumbs } from '@/hooks/useBreadcrumbs';
import {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import React, { memo } from 'react';

function HomePage() {
  const {
    user,
    isAuthLoading,
    isAuthenticated,
  } = useHomePage();
  
  const breadcrumbs = useBreadcrumbs();

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
      <div className="flex h-full bg-[#F5F3F2] font-inter">
        {/* Sidebar */}
        <DashboardSidebar />
        
        {/* Main Content Area */}
        <div className="flex-1 ml-[20px] overflow-y-auto overflow-x-hidden min-h-full">
          {/* Breadcrumbs */}
          <div className="px-7 pt-4 pb-2">
            <Breadcrumb>
              <BreadcrumbList>
                {breadcrumbs.map((crumb, index) => (
                  <React.Fragment key={index}>
                    <BreadcrumbItem>
                      {crumb.href ? (
                        <BreadcrumbLink href={crumb.href} className="font-inter font-medium text-[16px] text-[#a7a7a7] hover:text-[#0f0901]">
                          {crumb.label}
                        </BreadcrumbLink>
                      ) : (
                        <BreadcrumbPage className="font-inter font-medium text-[16px] text-[#0f0901]">
                          {crumb.label}
                        </BreadcrumbPage>
                      )}
                    </BreadcrumbItem>
                    {index < breadcrumbs.length - 1 && <BreadcrumbSeparator />}
                  </React.Fragment>
                ))}
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          
          {/* Content will be rendered here via Outlet */}
          <Outlet />
        </div>
      </div>
    );
}

export default memo(HomePage);
