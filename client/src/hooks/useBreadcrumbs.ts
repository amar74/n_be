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
    }

    return crumbs;
  }, [location.pathname, accountDetail, accountId]);

  return breadcrumbs;
}
