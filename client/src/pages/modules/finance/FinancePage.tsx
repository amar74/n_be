import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function FinancePage() {
  return (
    <ComingSoon 
      moduleId="finance" 
      moduleName="Finance" 
    />
  );
}

export default memo(FinancePage);
