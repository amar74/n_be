import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/lib/supabase';
import { apiClient } from '@/services/api/client';

export function useDashboardSidebar() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleLogout = useCallback(async () => {
    try {
      await supabase.auth.signOut();
      localStorage.removeItem('authToken');
      delete apiClient.defaults.headers.common['Authorization'];
      
      toast({
        title: 'Logged Out',
        description: 'You have been successfully logged out.',
      });
      
      navigate('/auth/login', { replace: true });
    } catch (error) {
      console.error('❌ DashboardSidebar: Logout failed:', error);
      toast({
        title: 'Logout Error',
        description: 'There was an issue logging out. Please try again.',
        variant: 'destructive',
      });
      // Still navigate to login even if logout fails
      navigate('/auth/login', { replace: true });
    }
  }, [navigate, toast]);

  return {
    handleLogout,
  };
}
