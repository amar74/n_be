import { Outlet } from 'react-router-dom';
import { useAuth } from '@hooks/useAuth';
import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navigation from '@components/Navigation';
import { Toaster } from '@/components/ui/toaster';

export default function MainLayout() {
  const { user, backendUser, isAuthenticated, initialAuthComplete } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Only handle redirects after initial auth is complete
    if (!initialAuthComplete) return;
    // If not authenticated with Supabase, redirect to login
    if (!user) {
      navigate('/auth/login', { replace: true });
      return;
    }

    // If Supabase auth exists but backend auth failed, redirect to login
    if (user && !isAuthenticated) {
      navigate('/auth/login', { replace: true });
      return;
    }
    if (!backendUser) return
    if (!isAuthenticated) return

    // Check for organization requirement after backend authentication is complete
    const currentPath = location.pathname;

    // If user doesn't have org_id and isn't already on org creation or auth pages
    if (
      (backendUser.org_id === null) &&
      !currentPath.startsWith('/organization/create') &&
      !currentPath.startsWith('/auth/')
    ) {
      console.info('User has no organization, redirecting to organization creation');
      navigate('/organization/create', { replace: true });
      return;
    }

    // If user has org_id but is on organization create page, redirect to home
    if (backendUser.org_id && currentPath.startsWith('/organization/create')) {
      console.info('User already has organization, redirecting to home');
      navigate('/', { replace: true });
      return;
    }
  }, [user, isAuthenticated, backendUser, initialAuthComplete, navigate, location.pathname]);

  // Show loading only during initial auth check
  if (!initialAuthComplete) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If no user or not authenticated, will redirect in useEffect
  if (!user || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="text-gray-600">Redirecting...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Navigation />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
      <Toaster />
    </div>
  );
}
