import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  PhoneCall,
  MapPin,
  Globe,
  Calendar,
  PencilSimpleLine,
  DotsThreeVertical,
  UserCircle,
  ChartLineUp,
  Gear,
  House,
  CaretRight,
  ShieldCheckered,
} from 'phosphor-react';
import { useToast } from '@/hooks/useToast';
import { useMyOrganization } from '@/hooks/useOrganizations';
import { useAuth } from '@/hooks/useAuth';
import type { Organization } from '@/types/orgs';
import OrganizationTeamSection from '@/components/OrganizationTeamSection';
import image from '@/assets/image.png';

export default function OrganizationPage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  // Use centralized hooks following Development.md patterns
  const organizationQuery = useMyOrganization();
  const { authState } = useAuth();

  const organization = organizationQuery.data;
  const isLoading = organizationQuery.isLoading;
  const error = organizationQuery.error;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const isAdmin = authState.user?.role === 'admin';

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F5F3F2]">
        <div className="max-w-5xl mx-auto px-4 md:px-20 py-12">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ED8A09]"></div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !organization) {
    return (
      <div className="min-h-screen bg-[#F5F3F2]">
        <div className="max-w-5xl mx-auto px-4 md:px-20 py-12">
          <Card className="rounded-3xl shadow-sm bg-white border-none">
            <CardContent className="p-8 text-center">
              <div className="text-red-600 mb-4">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <img src={image} alt="buildings-icon" className="h-8 w-8" />
                </div>
                <h2 className="text-xl font-medium mb-2">Organization Not Found</h2>
                <p className="text-sm">{error?.message || 'Unable to load organization details'}</p>
              </div>
              <Button
                onClick={() => organizationQuery.refetch()}
                className="bg-[#ED8A09] hover:bg-[#ED8A09]/90 text-white"
              >
                Try Again
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F5F3F2]">
      {/* Main Content */}
      <main className="p-2">
        <div className="max-w-5xl mx-auto px-4 md:px-20">
          {/* Breadcrumb just above card */}
          <div className="text-sm text-gray-500 mb-3 flex flex-wrap gap-1 items-center">
            <House size={18} className="text-gray-700" />
            <CaretRight size={16} className="text-gray-700" />
            <Link to="/" className="hover:text-[#ED8A09]">
              Profile
            </Link>
            <CaretRight size={16} className="text-gray-700" />
            Organization Detail
          </div>

          <Card className="rounded-3xl shadow-sm bg-white border-none">
            <CardContent className="p-6">
              {/* Top Section */}
              <div className="flex flex-col md:flex-row md:items-start justify-between mb-6 border-b pb-4 border-gray-200 gap-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-[#EBEBEB] rounded-full flex items-center justify-center">
                    <img src={image} alt="buildings-icon" className="h-8 w-8" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold break-words">{organization.name}</h2>
                    <Badge className="bg-green-100 text-[#0C8102] mt-2 rounded-xl flex items-center gap-2">
                      <span className="rounded-full w-3 h-3 bg-[#0C8102]"></span>
                      <span className="text-sm">Active Organization</span>
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {isAdmin && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="rounded-full bg-gray-50 hover:bg-gray-100"
                      onClick={() => navigate('/organization/update')}
                    >
                      <PencilSimpleLine className="w-4 h-4" />
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="rounded-full bg-gray-50 hover:bg-gray-100"
                    onClick={() => {
                      toast.info('Settings', {
                        description: 'Organization settings feature coming soon!',
                        duration: 3000,
                      });
                    }}
                  >
                    <DotsThreeVertical className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Admin + Created On */}
              <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-2">
                <Badge
                  className={`rounded-2xl px-3 py-2 flex items-center gap-1 ${
                    isAdmin ? 'bg-[#ED8A091A] text-[#ED8A09]' : 'bg-blue-50 text-blue-700'
                  }`}
                >
                  <ShieldCheckered className="w-4 h-4" />
                  {isAdmin ? 'Administrator' : 'Member'}
                </Badge>
                <div className="flex flex-row gap-2 items-center text-sm">
                  <span className="text-gray-500 text-sm font-semibold">Created on</span>
                  <Calendar className="w-4 h-4" />
                  <span className="font-medium">{formatDate(organization.created_at)}</span>
                </div>
              </div>

              {/* Info + Quick Actions in flex */}
              <div className="flex flex-col md:flex-row gap-8">
                {/* Left Column */}
                <div className="w-full flex-1 space-y-4 rounded-3xl p-6 border-gray-200 border">
                  <div className="border-b border-gray-200 pb-2">
                    <h3 className="font-semibold mb-2">Company Website</h3>
                    <div className="flex items-center gap-2">
                      <Globe className="w-4 h-4 text-gray-600" />
                      {organization.website ? (
                        <a
                          href={organization.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline text-blue-600 break-words"
                        >
                          {organization.website}
                        </a>
                      ) : (
                        <span className="text-gray-500">Not specified</span>
                      )}
                    </div>
                  </div>

                  <div className="border-b border-gray-200 pb-2">
                    <h3 className="font-semibold mb-2">Organization Address</h3>
                    <div className="flex items-start gap-2 text-gray-600">
                      <MapPin className="w-4 h-4 mt-1" />
                      {organization.address ? (
                        <span>
                          {organization.address.line1}
                          {organization.address.line2 && (
                            <>
                              <br />
                              {organization.address.line2}
                            </>
                          )}
                          {organization.address.pincode && (
                            <>
                              <br />
                              PIN: {organization.address.pincode}
                            </>
                          )}
                        </span>
                      ) : (
                        <span className="text-gray-500">Not specified</span>
                      )}
                    </div>
                  </div>

                  <div className="border-b border-gray-200 pb-2">
                    <h3 className="font-semibold mb-2">Contact Information</h3>
                    <div className="flex items-center gap-2 text-gray-600">
                      <PhoneCall className="w-4 h-4" />
                      {organization.contact?.email ? (
                        <span>{organization.contact.email}</span>
                      ) : (
                        <span className="text-gray-500">Not specified</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-2">Last Updated</h3>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(organization.created_at)}</span>
                    </div>
                  </div>
                </div>

                {/* Right Column - Quick Actions */}
                <div className="w-full md:w-1/2 rounded-3xl p-6 border-gray-200 border">
                  <h3 className="font-semibold text-xl mb-4 border-b pb-4 border-gray-200">
                    Quick Actions
                  </h3>
                  <div className="space-y-4">
                    <Button
                      variant="ghost"
                      className="w-full justify-start rounded-xl px-4 py-3 text-gray-700 hover:text-orange-500 hover:bg-gray-100"
                      onClick={() => navigate('/module/accounts')}
                    >
                      <UserCircle className="w-4 h-4 mr-2" />
                      View Accounts
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start rounded-xl px-4 py-3 text-gray-700 hover:text-orange-500 hover:bg-gray-100"
                      onClick={() => {
                        toast.info('Reports', {
                          description: 'Reports feature coming soon!',
                          duration: 3000,
                        });
                      }}
                    >
                      <ChartLineUp className="w-4 h-4 mr-2" />
                      View Reports
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start rounded-xl px-4 py-3 text-gray-700 hover:text-orange-500 hover:bg-gray-100"
                      onClick={() => {
                        toast.info('Settings', {
                          description: 'Settings management feature coming soon!',
                          duration: 3000,
                        });
                      }}
                    >
                      <Gear className="w-4 h-4 mr-2" />
                      Manage Settings
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Admin Notice - only show for non-admins */}
          {!isAdmin && (
            <Card className="rounded-3xl shadow-sm bg-blue-50 border-blue-200 mt-6">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <ShieldCheckered className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-medium text-blue-900 mb-1">Organization Management</h4>
                    <p className="text-sm text-blue-700">
                      Only organization administrators can edit organization details. Contact your
                      admin if changes are needed.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Organization Team Section */}
          <div className="mt-8">
            <OrganizationTeamSection />
          </div>
        </div>
      </main>
    </div>
  );
}
