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
    path: '/module/opportunities',
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
    path: '/module/proposals',
    icon: FileText,
  },
  {
    id: 'resources',
    name: 'Resources',
    path: '/module/resources',
    icon: Users,
  },
  {
    id: 'contracts',
    name: 'Contracts',
    path: '/module/contracts',
    icon: FileCheck,
  },
  {
    id: 'projects',
    name: 'Projects',
    path: '/module/projects',
    icon: Calendar,
  },
  {
    id: 'finance',
    name: 'Finance',
    path: '/module/finance',
    icon: Calculator,
  },
  {
    id: 'procurement',
    name: 'Procurements',
    path: '/module/procurement',
    icon: ShoppingCart,
  },
  {
    id: 'kpi',
    name: "KPI's",
    path: '/module/kpis',
    icon: BarChart3,
  },
];
