import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@hooks/useAuth';
import { useEffect } from 'react';

export default function AdminLayout() {
  const { user, isAuthenticated, initialAuthComplete } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!initialAuthComplete) return;

    if (!user || !isAuthenticated) {
      navigate('/admin/signin', { replace: true, state: { from: location.pathname } });
    }
  }, [user, isAuthenticated, initialAuthComplete, navigate, location.pathname]);

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
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white border-r border-gray-200 p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800">Admin</h2>
          <p className="text-sm text-gray-500">Management Panel</p>
        </div>
        <nav className="space-y-2">
          <Link to="/admin/dashboard" className="block px-3 py-2 rounded-md text-gray-700 hover:bg-gray-100">
            Dashboard
          </Link>
        </nav>
      </aside>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  );
}


