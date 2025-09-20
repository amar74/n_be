import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function OpportunitiesPage() {
  return (
    <ComingSoon 
      moduleId="opportunities" 
      moduleName="Opportunities" 
    />
  );
}

export default memo(OpportunitiesPage);
