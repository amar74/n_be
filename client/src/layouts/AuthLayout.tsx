import { Outlet } from 'react-router-dom';
import { useAuth } from '@hooks/useAuth';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom';

export default function AuthLayout() {
  const { user, initialAuthComplete } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // If user is already authenticated, redirect to main app immediately
    // Global toast service will ensure toasts persist across navigation
    if (user && location.pathname === '/auth/login') {
      navigate('/');
    }
  }, [user, location.pathname]);

  if (!initialAuthComplete) {
    return (
      <div className="w-fullmin-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="relative">
      <Outlet />
    </div>
  );
}
