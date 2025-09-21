import { memo } from 'react';
import { ComingSoon } from '@/components/ComingSoon';

function ProjectsPage() {
  return (
    <ComingSoon 
      moduleId="projects" 
      moduleName="Projects" 
    />
  );
}

export default memo(ProjectsPage);
