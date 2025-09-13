import { Link, useLocation } from 'react-router-dom';
import { 
  Target, 
  Building2, 
  FileText, 
  Users, 
  FileCheck, 
  Calendar, 
  Calculator, 
  ShoppingCart, 
  BarChart3,
  LogOut
} from 'lucide-react';
import { useDashboardSidebar } from './useDashboardSidebar';
import { memo } from 'react';

function DashboardSidebar() {
  const location = useLocation();
  const { handleLogout } = useDashboardSidebar();

  const navigationItems = [
    {
      id: 'opportunities',
      name: 'Opportunities',
      path: '/opportunities',
      icon: Target,
    },
    {
      id: 'accounts',
      name: 'Accounts',
      path: '/module/accounts',
      icon: Building2,
    },
    {
      id: 'proposals',
      name: 'Proposals',
      path: '/proposals',
      icon: FileText,
    },
    {
      id: 'resources',
      name: 'Resources',
      path: '/resources',
      icon: Users,
    },
    {
      id: 'contracts',
      name: 'Contracts',
      path: '/contracts',
      icon: FileCheck,
    },
    {
      id: 'projects',
      name: 'Projects',
      path: '/projects',
      icon: Calendar,
    },
    {
      id: 'finance',
      name: 'Finance',
      path: '/finance',
      icon: Calculator,
    },
    {
      id: 'procurement',
      name: 'Procurements',
      path: '/procurement',
      icon: ShoppingCart,
    },
    {
      id: 'kpi',
      name: "KPI's",
      path: '/kpis',
      icon: BarChart3,
    },
  ];

  const isActiveRoute = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="bg-white box-border content-stretch flex flex-col gap-44 items-start justify-start overflow-clip pb-7 pt-0 px-0 relative rounded-br-[28px] rounded-tr-[28px] size-full w-[260px] h-screen fixed left-0">
      <div className="content-stretch flex flex-col gap-2 items-start justify-start relative shrink-0 w-full">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = isActiveRoute(item.path);
          
          return (
            <Link
              key={item.id}
              to={item.path}
              className={`box-border content-stretch flex gap-3 h-[60px] items-center justify-start px-7 py-5 relative shrink-0 w-full transition-colors duration-200 hover:bg-gray-50 ${
                isActive ? 'bg-white border-b-2 border-[#0f0901]' : ''
              }`}
            >
              <div className="relative shrink-0 size-6">
                <Icon className={`w-6 h-6 ${isActive ? 'text-[#0f0901]' : 'text-[#6e6e6e]'}`} />
              </div>
              <div className={`font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 text-[16px] text-nowrap ${
                isActive ? 'text-[#0f0901]' : 'text-[#6e6e6e]'
              }`}>
                <p className="leading-[normal] whitespace-pre">{item.name}</p>
              </div>
            </Link>
          );
        })}
      </div>
      
      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="box-border content-stretch flex gap-3 h-[60px] items-center justify-start px-7 py-5 relative rounded-[19px] shrink-0 w-full transition-colors duration-200 hover:bg-gray-50"
      >
        <div className="relative shrink-0 size-6">
          <LogOut className="w-6 h-6 text-[#0f0901]" />
        </div>
        <div className="font-['Inter:Semi_Bold',_sans-serif] font-semibold leading-[0] not-italic relative shrink-0 text-[#0f0901] text-[18px] text-center text-nowrap">
          <p className="leading-[normal] whitespace-pre">Log-out</p>
        </div>
      </button>
    </div>
  );
}

export default memo(DashboardSidebar);
