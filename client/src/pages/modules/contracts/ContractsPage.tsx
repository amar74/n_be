import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function ContractsPage() {
  return (
    <ComingSoon 
      moduleId="contracts" 
      moduleName="Contracts" 
    />
  );
}

export default memo(ContractsPage);
