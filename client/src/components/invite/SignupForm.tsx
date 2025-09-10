import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Mail, Shield, Building2, Loader2 } from 'lucide-react';
import type { AcceptInviteResponse } from '@/types/orgs';

interface SignupFormProps {
  inviteData: AcceptInviteResponse;
  isSigningUp: boolean;
  onSubmit: (password: string) => Promise<void>;
}

// Type guard to ensure invite data is valid
function isValidInviteData(data: AcceptInviteResponse | null): data is AcceptInviteResponse {
  return !!(data && data.email && data.role && data.org_id);
}

export function SignupForm({ inviteData, isSigningUp, onSubmit }: SignupFormProps) {
  const [password, setPassword] = useState('');

  // Guard clause - early return if invalid invite data
  if (!isValidInviteData(inviteData)) {
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim()) return;
    
    await onSubmit(password);
    setPassword('');
  };

  const formattedRole = inviteData.role.charAt(0).toUpperCase() + inviteData.role.slice(1);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 p-3 bg-green-100 rounded-full w-fit">
            <Building2 className="h-6 w-6 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-[#1D1D1F]">
            Create Your Account
          </CardTitle>
          <CardDescription>
            Your invitation has been accepted. Now create your password to complete the signup process.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  type="email"
                  value={inviteData.email}
                  disabled
                  className="pl-10 bg-gray-50"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <div className="relative">
                <Shield className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="role"
                  value={formattedRole}
                  disabled
                  className="pl-10 bg-gray-50 capitalize"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                minLength={6}
              />
            </div>

            <Button
              type="submit"
              className="w-full bg-[#0D9488] hover:bg-[#0D9488]/90"
              disabled={isSigningUp || !password.trim()}
            >
              {isSigningUp ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
