import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useUserPermissions } from '@/hooks/useUserPermissions';
import type { 
  UserPermissionUpdateRequest, 
  UserWithPermissionsResponse,
  User,
  PermissionCategory
} from '@/types/userPermissions';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Users, Shield, Settings, RefreshCw } from 'lucide-react';

const PERMISSIONS = [
  { key: 'accounts', label: 'Accounts' },
  { key: 'opportunities', label: 'Opportunities' },
  { key: 'proposals', label: 'Proposals' },
];
const ACTIONS = ['view', 'edit'];
type PermissionAction = 'view' | 'edit';

type PermissionState = Record<string, { [K in PermissionCategory]: PermissionAction[] }>;

export default function UserPermissionsSection() {
  const [permissions, setPermissions] = useState<PermissionState>({});
  const [saving, setSaving] = useState<string | null>(null);

  // Use TanStack Query hooks
  const { 
    useUserPermissionsList, 
    updateUserPermission, 
    isUpdating 
  } = useUserPermissions();

  // Fetch users with permissions
  const { 
    data: usersWithPermissions = [], 
    isLoading: loading, 
    error,
    refetch
  } = useUserPermissionsList();

  // Initialize permissions state when data loads
  React.useEffect(() => {
    if (usersWithPermissions.length > 0) {
      const state: PermissionState = {};
      usersWithPermissions.forEach(userWithPermission => {
        state[userWithPermission.user.id] = {
          accounts: userWithPermission.permissions.accounts || [],
          opportunities: userWithPermission.permissions.opportunities || [],
          proposals: userWithPermission.permissions.proposals || [],
        };
      });
      setPermissions(state);
    }
  }, [usersWithPermissions]);

  // Calculate stats from current permissions state (this will update when permissions change)
  const totalUsers = usersWithPermissions.length;
  const activePermissions = Object.values(permissions).reduce((total, userPermissions) => {
    return total + 
      (userPermissions.accounts?.length || 0) + 
      (userPermissions.opportunities?.length || 0) + 
      (userPermissions.proposals?.length || 0);
  }, 0);
  const permissionCategories = PERMISSIONS.length;

  // Check if any user is currently being saved
  const isAnyUserSaving = Object.keys(saving ? { [saving]: true } : {}).length > 0;

  const handleCheck = (userid: string, perm: PermissionCategory, action: string) => {
    setPermissions(prev => ({
      ...prev,
      [userid]: {
        ...prev[userid],
        [perm]: prev[userid]?.[perm]?.includes(action as PermissionAction)
          ? prev[userid][perm].filter(a => a !== action)
          : [...(prev[userid]?.[perm] || []), action],
      },
    }));
  };

  const handleSave = async (userid: string) => {
    setSaving(userid);
    const permission = permissions[userid];
    const req: UserPermissionUpdateRequest = {
      accounts: permission.accounts,
      opportunities: permission.opportunities,
      proposals: permission.proposals,
    };
    try {
      await updateUserPermission({ userid, data: req });
      // TanStack Query will automatically update the cache and refetch
      // The permissions state will be updated when the new data comes in
    } catch (e) {
      // Error handling is done in the mutation
    } finally {
      setSaving(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FCFCFC] font-['Inter',_system-ui,_-apple-system,_sans-serif]">
        <div className="max-w-7xl mx-auto px-8 sm:px-12 lg:px-16 py-12">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-[#0D9488] mx-auto mb-4" />
              <p className="text-lg text-[#1D1D1F]">Loading user permissions...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#FCFCFC] font-['Inter',_system-ui,_-apple-system,_sans-serif]">
        <div className="max-w-7xl mx-auto px-8 sm:px-12 lg:px-16 py-12">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="text-red-500 mb-4">
                <Shield className="h-8 w-8 mx-auto mb-2" />
                <p className="text-lg">Failed to load user permissions</p>
                <p className="text-sm text-gray-500 mt-2">
                  {error instanceof Error ? error.message : 'An error occurred'}
                </p>
              </div>
              <Button onClick={() => refetch()} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FCFCFC] font-['Inter',_system-ui,_-apple-system,_sans-serif]">
      <div className="max-w-7xl mx-auto px-8 sm:px-12 lg:px-16 py-12">
        {/* Back Button */}
        <div className="mb-12">
          <Link
            to="/module/accounts"
            className="inline-flex items-center px-6 py-3 text-[#1D1D1F] hover:text-[#0D9488] hover:bg-[#F3F4F6] rounded-md transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 font-medium overflow-wrap-break-word"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            <span>Back to Accounts</span>
          </Link>
        </div>

        {/* Header Section */}
        <div className="flex justify-between items-center mb-12">
          <div>
            <h2 className="text-4xl font-medium text-[#1D1D1F] mb-4 text-center overflow-wrap-break-word">
              User Permissions
            </h2>
            <p className="text-lg text-[#1D1D1F] leading-relaxed font-normal overflow-wrap-break-word">
              Manage user permissions for accounts, opportunities, and proposals
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-6">
            <Button
              variant="outline"
              onClick={() => refetch()}
              className="bg-[#FCFCFC] hover:bg-[#F3F4F6] border-[#EFF1F3] text-[#1D1D1F] px-6 py-3 rounded-md font-medium transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 active:scale-99 shadow-[0_4px_16px_rgba(0,0,0,0.08)]"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <Card className={`border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg ${isAnyUserSaving ? 'opacity-75' : ''}`}>
            <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
              <Users className={`h-10 w-10 text-[#0D9488] mx-auto mb-4 ${isAnyUserSaving ? 'animate-pulse' : ''}`} />
              <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">
                Total Users
              </h4>
              <p className="text-3xl font-medium text-[#0D9488] mt-2">{totalUsers}</p>
            </CardContent>
          </Card>

          <Card className={`border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg ${isAnyUserSaving ? 'opacity-75' : ''}`}>
            <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
              <Shield className={`h-10 w-10 text-[#F59E0B] mx-auto mb-4 ${isAnyUserSaving ? 'animate-pulse' : ''}`} />
              <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">
                Active Permissions
              </h4>
              <p className="text-3xl font-medium text-[#F59E0B] mt-2">
                {activePermissions}
              </p>
            </CardContent>
          </Card>

          <Card className={`border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)] transition-all duration-300 ease-in-out hover:transform hover:-translate-y-0.5 hover:shadow-lg ${isAnyUserSaving ? 'opacity-75' : ''}`}>
            <CardContent className="p-8 text-center flex flex-col items-center justify-center h-full">
              <Settings className={`h-10 w-10 text-[#0D9488] mx-auto mb-4 ${isAnyUserSaving ? 'animate-pulse' : ''}`} />
              <h4 className="font-medium text-[#1D1D1F] mb-2 overflow-wrap-break-word">
                Permission Categories
              </h4>
              <p className="text-3xl font-medium text-[#0D9488] mt-2">{permissionCategories}</p>
            </CardContent>
          </Card>
        </div>

        {/* Permissions Table */}
        <Card className="border border-[#EFF1F3] bg-[#FCFCFC] rounded-md shadow-[0_4px_16px_rgba(0,0,0,0.08)]">
          <CardHeader className="p-8">
            <CardTitle className="text-2xl font-medium text-[#1D1D1F] flex items-center">
              <Shield className="h-6 w-6 mr-3 text-[#0D9488]" />
              Permission Assignment Matrix
            </CardTitle>
          </CardHeader>
          <CardContent className="p-8 pt-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-[#1D1D1F] font-medium">User</TableHead>
                    <TableHead className="text-[#1D1D1F] font-medium">Role</TableHead>
                    {PERMISSIONS.map(perm => (
                      <TableHead key={perm.key} colSpan={ACTIONS.length} className="text-[#1D1D1F] font-medium text-center">
                        {perm.label}
                      </TableHead>
                    ))}
                    <TableHead className="text-[#1D1D1F] font-medium">Action</TableHead>
                  </TableRow>
                  <TableRow>
                    <TableHead />
                    <TableHead />
                    {PERMISSIONS.map(perm => (
                      ACTIONS.map(action => (
                        <TableHead key={perm.key + action} className="text-center text-sm text-gray-600">
                          {action}
                        </TableHead>
                      ))
                    ))}
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {usersWithPermissions.map(userWithPermission => (
                    <TableRow key={userWithPermission.user.id} className="hover:bg-[#F3F4F6] transition-colors">
                      <TableCell>
                        <div>
                          <div className="font-medium text-[#1D1D1F]">{userWithPermission.user.email}</div>
                          <div className="text-sm text-gray-500">ID: {userWithPermission.user.id.slice(0, 8)}...</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant="outline" 
                          className="bg-[#0D9488]/10 text-[#0D9488] border-[#0D9488]/20"
                        >
                          {userWithPermission.user.role}
                        </Badge>
                      </TableCell>
                      {PERMISSIONS.map(perm => (
                        ACTIONS.map(action => (
                          <TableCell key={perm.key + action} className="text-center">
                            <Checkbox
                              checked={permissions[userWithPermission.user.id]?.[perm.key as PermissionCategory]?.includes(action as PermissionAction) || false}
                              onCheckedChange={() => handleCheck(userWithPermission.user.id, perm.key as PermissionCategory, action)}
                              className="data-[state=checked]:bg-[#0D9488] data-[state=checked]:border-[#0D9488]"
                            />
                          </TableCell>
                        ))
                      ))}
                      <TableCell>
                        <Button 
                          size="sm" 
                          onClick={() => handleSave(userWithPermission.user.id)} 
                          disabled={saving === userWithPermission.user.id || isUpdating}
                          className="bg-[#0D9488] hover:bg-[#0D9488]/90 text-white"
                        >
                          {saving === userWithPermission.user.id ? (
                            <>
                              <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            'Save'
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            
            {usersWithPermissions.length === 0 && !loading && (
              <div className="text-center text-gray-500 py-12">
                <Users className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg">No users found in your organization.</p>
                <p className="text-sm mt-2">Contact your administrator to add users to your organization.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
