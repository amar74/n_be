import React from 'react';
import { Buildings, Calendar, TrendUp, CurrencyCircleDollar } from 'phosphor-react';

const OverviewMetrics: React.FC = () => {
  const metrics = [
    {
      icon: CurrencyCircleDollar,
      label: 'Total Value',
      value: '$8.5M',
    },
    {
      icon: TrendUp,
      label: 'Opportunities',
      value: '1',
    },
    {
      icon: Calendar,
      label: 'Last Contact',
      value: '2024-12-01',
    },
    {
      icon: Buildings,
      label: 'Client Type',
      value: 'Tier 1',
    },    
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 xl:gap-6 mb-4">
      {metrics.map((metric, index) => (
        <div
          key={index}
          className="bg-white p-3 xl:p-4 rounded-2xl border-[2px] border-gray-300 hover:shadow-sm transition-shadow w-full"
        >
          <div className="flex items-center space-x-3">
            <div className="p-4 rounded-full bg-gray-100 text-orange-400">
              <metric.icon size={18} weight="fill" />
            </div>
            <div className="flex-1">
              <div className="text-xs text-gray-500 font-medium">{metric.label}</div>
              <div>
                <span className="text-base xl:text-lg font-bold text-gray-900">
                  {metric.value}
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default OverviewMetrics;
