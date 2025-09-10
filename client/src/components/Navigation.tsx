import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '@hooks/useAuth';
import { Building2, ChevronDown, User, LogOut, Home, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useToast } from '@/hooks/useToast';
import logo from '@/assets/logo.png';
import john from '@/assets/john.png';

export default function Navigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false);
  const [isSigningOut, setIsSigningOut] = useState(false);

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  const handleSignOut = async () => {
    if (isSigningOut) return; // Prevent multiple clicks

    try {
      setIsSigningOut(true);
      setIsUserDropdownOpen(false);

      // Show signing out toast immediately
      toast.info('Signing out...', {
        description: 'Please wait while we sign you out.',
        duration: 2000,
      });

      const { error } = await signOut();

      if (error) {
        toast.error('Sign Out Failed', {
          description: error.message,
          duration: 4000,
        });
        setIsSigningOut(false);
      } else {
        // Show success toast
        toast.success('Signed out successfully', {
          description: 'You have been signed out of your account.',
          duration: 3000,
        });

        // Navigate to login immediately after successful logout
        navigate('/auth/login', { replace: true });
      }
    } catch (err) {
      console.error('Sign out error:', err);
      toast.error('Sign Out Failed', {
        description: 'An unexpected error occurred while signing out.',
        duration: 4000,
      });
      setIsSigningOut(false);
    }
  };

  // Get user display name
  const getUserDisplayName = () => {
    if (isSigningOut) return 'Signing out...';
    const metadata = user?.user_metadata as Record<string, any> | undefined;
    if (metadata?.name) return metadata.name;
    if (user?.email) return user.email.split('@')[0];
    return 'User';
  };

  // Get user email
  const getUserEmail = () => {
    if (isSigningOut) return 'Please wait...';
    return user?.email || 'user@example.com';
  };

  return (
    <>
      <header className="px-6 py-4 flex items-center justify-between bg-[#F5F3F2]">
        {/* Left side - Logo */}
        <div className="flex items-center">
          <div className="flex items-center gap-3">
            <div>
              <Link to="/">
                <img src={logo} alt="Logo" className="w-36 h-10" />
              </Link>
            </div>
          </div>
        </div>

        {/* Right side - Notifications and user */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            className="relative text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded-full bg-white"
          >
            <Bell size={20} />
            <span className="absolute -top-0 -right-0 w-2 h-2 bg-red-500 rounded-full"></span>
          </Button>

          <div className="relative">
            <button
              onClick={() => setIsUserDropdownOpen(!isUserDropdownOpen)}
              className="flex items-center gap-3 hover:bg-gray-200 rounded-lg p-2 transition-colors"
              aria-expanded={isUserDropdownOpen}
              aria-haspopup="true"
            >
              <Avatar className="w-10 h-10">
                <AvatarImage src={john} alt={getUserDisplayName()} />
                <AvatarFallback className="bg-orange-500 text-white text-sm">
                  {getUserDisplayName().charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="hidden md:block text-left">
                <div className="text-sm font-medium text-gray-900">{getUserDisplayName()}</div>
                <div className="text-xs text-gray-500">{getUserEmail()}</div>
              </div>
              <ChevronDown className="h-4 w-4 text-gray-600" />
            </button>

            {/* Dropdown menu */}
            {isUserDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                <div className="py-1">
                  {/* User info header */}
                  <div className="px-4 py-3 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900">{getUserDisplayName()}</p>
                    <p className="text-sm text-gray-500 truncate">{user?.email}</p>
                  </div>

                  {/* Navigation items */}
                  <div className="border-b border-gray-100">
                    <Link
                      to="/"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setIsUserDropdownOpen(false)}
                    >
                      <Home className="h-4 w-4 mr-2" />
                      Dashboard
                    </Link>
                    <Link
                      to="/organization"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setIsUserDropdownOpen(false)}
                    >
                      <Building2 className="h-4 w-4 mr-2" />
                      Organization
                    </Link>
                  </div>

                  {/* Action items */}
                  <button
                    onClick={handleSignOut}
                    disabled={isSigningOut}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    {isSigningOut ? 'Signing out...' : 'Sign out'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Click outside to close dropdown */}
        {isUserDropdownOpen && (
          <div className="fixed inset-0 z-40" onClick={() => setIsUserDropdownOpen(false)} />
        )}
      </header>

      {/* Content is rendered by parent layout's Outlet */}
    </>
  );
}
