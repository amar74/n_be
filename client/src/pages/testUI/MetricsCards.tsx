import React from 'react';
import { Buildings, Heartbeat, Warning, TrendUp, Coins } from 'phosphor-react';

const MetricsCards: React.FC = () => {
  const metrics = [
    {
      icon: Buildings,
      label: 'Total Accounts',
      value: '15',
    },
    {
      icon: Heartbeat,
      label: 'AI Health Score',
      value: '78%',
      subtitle: 'Average',
    },
    {
      icon: Warning,
      label: 'High Risk',
      value: '3',
      subtitle: 'Require attention',
    },
    {
      icon: TrendUp,
      label: 'Growing',
      value: '7',
      subtitle: 'Positive Trend',
    },
    {
      icon: Coins,
      label: 'Total Value',
      value: '$92.6M',
      subtitle: 'Portfolio',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 xl:gap-6 mb-4 xl:mb-8">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-white p-2 xl:p-3 rounded-2xl border-[2px] border-gray-400 hover:shadow-sm transition-shadow " >
          <div className="flex items-center space-x-2 xl:space-x-3">
            <div className="p-4 rounded-full bg-gray-100 text-orange-400">
              <metric.icon  size={20} weight='fill' />
            </div>
            <div className="flex-1">
              <div className="text-xs text-gray-500 font-medium truncate">{metric.label}</div>
              <div>
                <span className='text-base xl:text-lg font-bold text-orange-400'>{metric.value}</span>
                 <span className=' mx-1.5 text-sm font-semibold text-gray-800'>{metric.subtitle}</span></div>
              {/* {metric.subtitle && (
                <div className="text-xs text-gray-400 truncate">{metric.subtitle}</div>
              )} */}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricsCards;