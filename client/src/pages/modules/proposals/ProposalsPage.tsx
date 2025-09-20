import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function ProposalsPage() {
  return (
    <ComingSoon 
      moduleId="proposals" 
      moduleName="Proposals" 
    />
  );
}

export default memo(ProposalsPage);
