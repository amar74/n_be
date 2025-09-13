import { Card, CardContent } from '@/components/ui/card';
import {
  Building2,
  FileText,
  TrendingUp,
  Users,
  Calendar,
  FileCheck,
  ShoppingCart,
  Calculator,
  BarChart3,
  Target,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { memo } from 'react';

function DashboardWelcome() {
  const dashboardCards = [
    {
      id: 'opportunities',
      name: 'Opportunities',
      path: '/opportunities',
      icon: TrendingUp,
      bgClass: 'bg-green-100',
      hoverBgClass: 'group-hover:bg-green-200',
      iconTextClass: 'text-green-600',
      value: '24',
    },
    {
      id: 'accounts',
      name: 'Accounts',
      path: '/module/accounts',
      icon: Users,
      bgClass: 'bg-purple-100',
      hoverBgClass: 'group-hover:bg-purple-200',
      iconTextClass: 'text-purple-600',
      value: '45',
    },
    {
      id: 'proposals',
      name: 'Proposals',
      path: '/proposals',
      icon: FileText,
      bgClass: 'bg-blue-100',
      hoverBgClass: 'group-hover:bg-blue-200',
      iconTextClass: 'text-blue-600',
      value: '12',
    },
    {
      id: 'resources',
      name: 'Resources',
      path: '/resources',
      icon: Users,
      bgClass: 'bg-teal-100',
      hoverBgClass: 'group-hover:bg-teal-200',
      iconTextClass: 'text-teal-600',
      value: '156',
    },
    {
      id: 'contracts',
      name: 'Contracts',
      path: '/contracts',
      icon: FileCheck,
      bgClass: 'bg-emerald-100',
      hoverBgClass: 'group-hover:bg-emerald-200',
      iconTextClass: 'text-emerald-600',
      value: '28',
    },
    {
      id: 'projects',
      name: 'Projects',
      path: '/projects',
      icon: Calendar,
      bgClass: 'bg-cyan-100',
      hoverBgClass: 'group-hover:bg-cyan-200',
      iconTextClass: 'text-cyan-600',
      value: '18',
    },
    {
      id: 'finance',
      name: 'Finance',
      path: '/finance',
      icon: Calculator,
      bgClass: 'bg-rose-100',
      hoverBgClass: 'group-hover:bg-rose-200',
      iconTextClass: 'text-rose-600',
      value: '$12.4M',
    },
    {
      id: 'procurement',
      name: 'Procurement',
      path: '/procurement',
      icon: ShoppingCart,
      bgClass: 'bg-amber-100',
      hoverBgClass: 'group-hover:bg-amber-200',
      iconTextClass: 'text-amber-600',
      value: '$2.1M',
    },
    {
      id: 'kpi',
      name: "KPI's",
      path: '/kpis',
      icon: BarChart3,
      bgClass: 'bg-violet-100',
      hoverBgClass: 'group-hover:bg-violet-200',
      iconTextClass: 'text-violet-600',
      value: '25',
    },
  ];

  return (
    <div>
      {/* Compact Business Module Navigation */}
      <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-6 mb-12">
        {dashboardCards.map((item) => (
          <Card
            key={item.id}
            className="border bg-white rounded-lg transition-all duration-200 cursor-pointer group hover:transform hover:-translate-y-0.5 active:scale-98 border-[#E5E7EB] hover:border-[#3B82F6] shadow-[0_4px_6px_-1px_rgb(0_0_0_/_0.1),_0_2px_4px_-2px_rgb(0_0_0_/_0.1)] hover:shadow-lg"
          >
            <Link to={item.path}>
              <CardContent className="p-6 text-center flex flex-col items-center justify-center h-full">
                <div
                  className={`mx-auto ${item.bgClass} p-3 rounded-lg w-fit mb-3 ${item.hoverBgClass} transition-all duration-200`}
                >
                  <item.icon className={`h-5 w-5 ${item.iconTextClass}`} />
                </div>
                <h3 className="text-sm font-semibold text-[#111827] mb-2 text-center">
                  {item.name}
                </h3>
                <p className="text-sm text-[#1F2937]">{item.value}</p>
              </CardContent>
            </Link>
          </Card>
        ))}
      </div>

      {/* Divider Line */}
      <div className="border-b border-[#E5E7EB] mb-12"></div>

      {/* Welcome Message */}
      <div className="text-center py-12">
        <h3 className="text-xl font-semibold text-[#111827] mb-4">
          Select a module from the sidebar or cards above to get started
        </h3>
        <p className="text-[#1F2937] max-w-2xl mx-auto">
          Use the navigation sidebar on the left to access different modules of your business management system. 
          Each module provides comprehensive tools to manage different aspects of your organization.
        </p>
      </div>
    </div>
  );
}

export default memo(DashboardWelcome);
