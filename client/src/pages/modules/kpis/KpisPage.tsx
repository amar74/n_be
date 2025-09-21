import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function KpisPage() {
  return (
    <ComingSoon 
      moduleId="kpis" 
      moduleName="KPI's" 
    />
  );
}

export default memo(KpisPage);
