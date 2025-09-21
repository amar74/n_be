import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function ResourcesPage() {
  return (
    <ComingSoon 
      moduleId="resources" 
      moduleName="Resources" 
    />
  );
}

export default memo(ResourcesPage);
