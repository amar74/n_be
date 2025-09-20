import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { useAccountDetail } from './useAccounts';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export function useBreadcrumbs() {
  const location = useLocation();
  
  // Extract account ID from path if present
  const accountIdMatch = location.pathname.match(/\/module\/accounts\/([^\/]+)/);
  const accountId = accountIdMatch ? accountIdMatch[1] : null;
  
  // Get account data if we're on an account page
  const { accountDetail } = useAccountDetail(accountId || '');

  const breadcrumbs: BreadcrumbItem[] = useMemo(() => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const crumbs: BreadcrumbItem[] = [{ label: 'Dashboard' }];

    // Handle different route patterns
    if (pathSegments.includes('module')) {
      const moduleIndex = pathSegments.indexOf('module');
      const moduleType = pathSegments[moduleIndex + 1];
      
      if (moduleType === 'accounts') {
        crumbs.push({ 
          label: 'Accounts', 
          href: '/module/accounts' 
        });
        
        // If we have an account ID, add the account name
        if (accountId && accountDetail) {
          crumbs.push({ 
            label: accountDetail.client_name || 'Account Details'
          });
        }
      }
      // Add more module types as needed
    } else {
      // Handle direct module routes (without /module prefix)
      const firstSegment = pathSegments[0];
      
      switch (firstSegment) {
        case 'opportunities':
          crumbs.push({ label: 'Opportunities' });
          break;
        case 'proposals':
          crumbs.push({ label: 'Proposals' });
          break;
        case 'resources':
          crumbs.push({ label: 'Resources' });
          break;
        case 'contracts':
          crumbs.push({ label: 'Contracts' });
          break;
        case 'projects':
          crumbs.push({ label: 'Projects' });
          break;
        case 'finance':
          crumbs.push({ label: 'Finance' });
          break;
        case 'procurement':
          crumbs.push({ label: 'Procurements' });
          break;
        case 'kpis':
          crumbs.push({ label: "KPI's" });
          break;
      }
    }

    return crumbs;
  }, [location.pathname, accountDetail, accountId]);

  return breadcrumbs;
}
