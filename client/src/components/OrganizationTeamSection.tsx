import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, UserPlus, Shield, User, Crown, Loader2 } from 'lucide-react';
import { useOrganization } from '@/hooks/useOrganization';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import type { OrgMemberResponse } from '@/types/orgs';

const getRoleIcon = (role: string) => {
  switch (role.toLowerCase()) {
    case 'admin':
      return <Crown className="h-3 w-3" />;
    case 'manager':
    case 'dev':
      return <Shield className="h-3 w-3" />;
    default:
      return <User className="h-3 w-3" />;
  }
};

const getRoleBadgeStyle = (role: string) => {
  switch (role.toLowerCase()) {
    case 'admin':
      return 'bg-purple-50 text-purple-700 border-purple-300';
    case 'manager':
    case 'dev':
      return 'bg-blue-50 text-blue-700 border-blue-300';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-300';
  }
};

const getStatusBadgeStyle = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active':
      return 'bg-green-50 text-green-700 border-green-300';
    case 'pending':
      return 'bg-yellow-50 text-yellow-700 border-yellow-300';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-300';
  }
};

export default function OrganizationTeamSection() {
  const {
    members,
    totalMembersCount,
    isMembersLoading,
    membersError,
    inviteMember,
    isInviting: isInvitingAPI,
  } = useOrganization();
  const { authState } = useAuth();
  const { toast } = useToast();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('member');

  // Use role from proper AuthState structure
  const userRole = authState.user?.role;
  const isAdmin = typeof userRole === 'string' && userRole.toLowerCase() === 'admin';

  const handleInviteMember = (e: React.FormEvent) => {
    e.preventDefault();

    inviteMember(
      { email, role },
      {
        onSuccess: () => {
          toast({
            title: 'Success',
            description: 'Team member invited successfully.',
          });
          setIsModalOpen(false);
          setEmail('');
          setRole('member');
        },
        onError: (error: any) => {
          toast({
            title: 'Error',
            description: error?.response?.data?.message || 'Failed to invite team member.',
            variant: 'destructive',
          });
        },
      }
    );
  };
  if (isMembersLoading) {
    return (
      <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] mt-8">
        <CardContent className="p-6">
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-[#0D9488]" />
            <span className="ml-2 text-[#1D1D1F]/70">Loading team members...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (membersError) {
    return (
      <Card className="border border-red-200 bg-red-50 rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] mt-8">
        <CardContent className="p-6">
          <div className="text-center py-8">
            <p className="text-red-600">Failed to load team members</p>
            <p className="text-red-500 text-sm mt-1">
              {membersError instanceof Error ? membersError.message : 'Unknown error'}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] mt-8">
      <CardHeader className="p-6 pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-medium text-[#1D1D1F] flex items-center gap-2">
            <Users className="h-5 w-5 text-[#0D9488]" />
            Team Members
            <Badge
              variant="outline"
              className="bg-[#F3F4F6] text-[#1D1D1F]/70 border-[#EFF1F3] ml-2"
            >
              {totalMembersCount}
            </Badge>
          </CardTitle>
          {isAdmin && (
            <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
              <DialogTrigger asChild>
                <Button
                  className="bg-[#0D9488] hover:bg-[#0D9488]/90 text-white shadow-sm"
                  size="sm"
                >
                  <UserPlus className="h-4 w-4 mr-2" />
                  Add Member
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px] bg-white">
                <DialogHeader>
                  <DialogTitle>Invite Team Member</DialogTitle>
                  <DialogDescription>
                    Enter the email address and select a role for the person you'd like to invite to
                    your organization. Admin roles cannot be assigned through invitations.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleInviteMember}>
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="email" className="text-right">
                        Email
                      </Label>
                      <Input
                        id="email"
                        type="email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="member@example.com"
                        className="col-span-3"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="role" className="text-right">
                        Role
                      </Label>
                      <Select value={role} onValueChange={setRole}>
                        <SelectTrigger className="col-span-3">
                          <SelectValue placeholder="Select role" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="member">Member</SelectItem>
                          <SelectItem value="dev">Developer</SelectItem>
                          <SelectItem value="manager">Manager</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setIsModalOpen(false)}
                      disabled={isInvitingAPI}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={isInvitingAPI || !email.trim() || !role}
                      className="bg-[#0D9488] hover:bg-[#0D9488]/90"
                    >
                      {isInvitingAPI ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          Inviting...
                        </>
                      ) : (
                        'Send Invite'
                      )}
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-6 pt-2">
        <div className="space-y-4">
          {members.map((member, index) => (
            <div
              key={`${member.email}-${index}`}
              className="flex items-center justify-between p-4 rounded-md border border-[#EFF1F3] bg-[#FCFCFC] hover:bg-[#F9FAFB] transition-colors duration-200"
            >
              <div className="flex items-center space-x-4">
                <Avatar className="h-10 w-10">
                  <AvatarFallback className="bg-[#0D9488]/10 text-[#0D9488] font-medium">
                    {member.email.substring(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium text-[#1D1D1F]">{member.email}</h3>
                    <Badge
                      variant="outline"
                      className={`${getRoleBadgeStyle(member.role)} text-xs`}
                    >
                      {getRoleIcon(member.role)}
                      <span className="ml-1 capitalize">{member.role}</span>
                    </Badge>
                  </div>
                  <p className="text-sm text-[#1D1D1F]/70">{member.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge
                  variant="outline"
                  className={`${getStatusBadgeStyle(member.status)} text-xs`}
                >
                  {member.status}
                </Badge>
              </div>
            </div>
          ))}
          {members.length === 0 && (
            <div className="text-center py-8">
              <Users className="h-12 w-12 mx-auto mb-4 text-[#1D1D1F]/30" />
              <p className="text-[#1D1D1F]/70">No team members found</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
