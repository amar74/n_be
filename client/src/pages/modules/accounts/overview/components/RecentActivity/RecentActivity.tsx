import React from 'react';
import { FileText, Calendar, CheckCircle } from 'lucide-react';
import { RecentActivityItem } from '../../../AccountDetailsPage.types';

const iconMap = {
  FileText,
  Calendar,
  CheckCircle,
};

interface RecentActivityProps {
  activities: RecentActivityItem[];
}

export function RecentActivity({ activities }: RecentActivityProps) {
  return (
    <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] py-6 px-0 w-[561px]">
      <div className="flex flex-col gap-6 w-full">
        {/* Header */}
        <div className="px-6">
          <div className="flex flex-col gap-7">
            <div className="flex flex-col gap-2">
              <h2 className="font-inter font-bold text-[#0f0901] text-[24px] leading-normal">
                Recent Activity
              </h2>
            </div>
          </div>
        </div>

        {/* Activity List */}
        <div className="flex flex-col w-full">
          {activities.map((activity, index) => {
            const IconComponent = iconMap[activity.icon as keyof typeof iconMap];
            const isLast = index === activities.length - 1;
            
            return (
              <div
                key={activity.id}
                className={`flex gap-2 items-start justify-start p-6 w-full relative ${
                  !isLast ? 'border-b border-[#eaeaea]' : ''
                }`}
              >
                {/* Icon */}
                <div className="h-4 w-3 mt-1 flex-shrink-0">
                  <IconComponent 
                    className="h-4 w-4" 
                    style={{ color: activity.color || '#6c6c6c' }} 
                  />
                </div>

                {/* Content */}
                <div className="flex flex-col gap-2 flex-1 min-w-0">
                  <h3 className="font-inter font-semibold text-[#0f0901] text-[18px] leading-normal">
                    {activity.title}
                  </h3>
                  <div className="flex gap-3 items-start justify-start w-full">
                    <span className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
                      {activity.timestamp}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
