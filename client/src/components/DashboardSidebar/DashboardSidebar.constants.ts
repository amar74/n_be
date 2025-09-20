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
} from 'lucide-react';
import { NavigationItem } from './DashboardSidebar.types';

export const NAVIGATION_ITEMS: NavigationItem[] = [
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
