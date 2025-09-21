import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function ProcurementPage() {
  return (
    <ComingSoon 
      moduleId="procurement" 
      moduleName="Procurements" 
    />
  );
}

export default memo(ProcurementPage);
