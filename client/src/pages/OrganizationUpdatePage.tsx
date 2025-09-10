import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Form, FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form';
import {
  House,
  CaretRight,
  Calendar,
  ShieldCheckered,
  Buildings,
  Globe,
  MapPin,
  Envelope,
  Phone,
  Sparkle,
} from 'phosphor-react';
import { useToast } from '@/hooks/useToast';
import { useMyOrganization, useOrganizations } from '@/hooks/useOrganizations';
import { useAuth } from '@/hooks/useAuth';
import type { UpdateOrgFormData } from '@/types/orgs';
import image from '@/assets/image.png';

export default function OrganizationUpdatePage() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    organizationName: '',
    website: '',
    addressLine1: '',
    addressLine2: '',
    pincode: '',
    email: '',
    phone: '',
  });

  // Use centralized hooks following Development.md patterns
  const organizationQuery = useMyOrganization();
  const { authState } = useAuth();
  const { updateOrganization, isUpdating } = useOrganizations();

  const organization = organizationQuery.data;
  const isLoading = organizationQuery.isLoading;
  const error = organizationQuery.error;

  const form = useForm<UpdateOrgFormData>({
    defaultValues: {
      name: '',
      website: '',
      address: {
        line1: '',
        line2: '',
        pincode: undefined,
      },
      contact: {
        phone: '',
        email: '',
      },
    },
  });

  const {
    handleSubmit,
    formState: { isSubmitting },
  } = form;

  // Update form when organization data is loaded
  useEffect(() => {
    if (organization) {
      console.log('🔄 OrganizationUpdatePage: Loading organization data into form', {
        orgId: organization.id,
        orgName: organization.name,
      });

      // Update both form and formData state
      const organizationData = {
        name: organization.name,
        website: organization.website || '',
        address: {
          line1: organization.address?.line1 || '',
          line2: organization.address?.line2 || '',
          pincode: organization.address?.pincode || undefined,
        },
        contact: {
          phone: organization.contact?.phone || '',
          email: organization.contact?.email || '',
        },
      };

      form.reset(organizationData);

      setFormData({
        organizationName: organization.name,
        website: organization.website || '',
        addressLine1: organization.address?.line1 || '',
        addressLine2: organization.address?.line2 || '',
        pincode: organization.address?.pincode?.toString() || '',
        email: organization.contact?.email || '',
        phone: organization.contact?.phone || '',
      });
    }
  }, [organization, form]);

  // Redirect non-admin users
  useEffect(() => {
    if (!isLoading && authState.user && authState.user.role !== 'admin') {
      toast.error('Only administrators can edit organization details.');
      navigate('/organization');
    }
  }, [authState.user, isLoading, navigate, toast]);

  const onSubmit = async (data: UpdateOrgFormData) => {
    if (!organization) {
      toast.error('Organization data not loaded');
      return;
    }

    try {
      console.log('🚀 OrganizationUpdatePage: Starting organization update', {
        orgId: organization.id,
        orgName: data.name,
      });

      // Transform data to match the backend expected format
      const updateData: UpdateOrgFormData = {
        name: data.name?.trim(),
        website: data.website?.trim() || undefined,
        address: data.address
          ? {
              line1: data.address.line1?.trim(),
              line2: data.address.line2?.trim() || undefined,
              pincode: data.address.pincode || undefined,
            }
          : undefined,
        contact: data.contact
          ? {
              phone: data.contact.phone?.trim() || undefined,
              email: data.contact.email?.trim() || undefined,
            }
          : undefined,
      };

      await updateOrganization({ orgId: organization.id, data: updateData });

      console.log('✅ OrganizationUpdatePage: Organization updated successfully');

      toast.success('Organization updated successfully.');

      // Navigate back to organization page
      navigate('/organization');
    } catch (error: unknown) {
      console.error('❌ OrganizationUpdatePage: Failed to update organization:', error);
      // Error handling is already done in the centralized hook
    }
  };

  const handleFormDataChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Also update the react-hook-form state
    if (field === 'organizationName') {
      form.setValue('name', value);
    } else if (field === 'website') {
      form.setValue('website', value);
    } else if (field === 'addressLine1') {
      form.setValue('address.line1', value);
    } else if (field === 'addressLine2') {
      form.setValue('address.line2', value);
    } else if (field === 'pincode') {
      const numValue = value ? parseInt(value) : undefined;
      form.setValue('address.pincode', numValue);
    } else if (field === 'email') {
      form.setValue('contact.email', value);
    } else if (field === 'phone') {
      form.setValue('contact.phone', value);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F5F3F2] overflow-x-hidden">
        <main className="p-2">
          <div className="max-w-5xl mx-auto px-4 md:px-8">
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ED8A09]"></div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Error state or non-admin user
  if (error || !organization || !authState.user || authState.user.role !== 'admin') {
    return (
      <div className="min-h-screen bg-[#F5F3F2] overflow-x-hidden">
        <main className="p-2">
          <div className="max-w-5xl mx-auto px-4 md:px-8">
            <Card className="border border-red-200 bg-red-50 mt-8">
              <CardContent className="p-8 text-center">
                <div className="text-red-600 mb-4">
                  <h2 className="text-xl font-medium mb-2">
                    {authState.user?.role !== 'admin' ? 'Access Denied' : 'Organization Not Found'}
                  </h2>
                  <p className="text-sm">
                    {authState.user?.role !== 'admin'
                      ? 'Only administrators can edit organization details.'
                      : error?.message || 'Unable to load organization details'}
                  </p>
                </div>
                <Button
                  onClick={() => navigate('/organization')}
                  className="bg-[#ED8A09] hover:bg-[#ED8A09]/90 text-white"
                >
                  Back to Organization
                </Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F5F3F2] overflow-x-hidden">
      {/* Main Content */}
      <main className="p-2">
        <div className="max-w-5xl mx-auto px-4 md:px-8">
          {/* Breadcrumb */}
          <div className="text-sm text-gray-500 mb-3 flex flex-row gap-1 items-center flex-wrap">
            <House size={18} className="text-gray-700" />
            <CaretRight size={16} className="text-gray-700" /> Profile
            <CaretRight size={16} className="text-gray-700" /> Organization Detail
          </div>

          {/* Page Title */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-[#ED8A09]">Edit Organization Details</h1>
            <p className="text-gray-600 text-sm md:text-base">
              Update your organization details and information. Changes will be saved immediately.
            </p>
          </div>

          <Card className="rounded-3xl shadow-sm bg-white border-none">
            <CardContent className="p-6 md:p-8">
              {/* Organization Header */}
              <div className="flex flex-col lg:flex-row items-start lg:items-center gap-6 mb-8 justify-between">
                {/* Icon + Title */}
                <div className="flex items-center gap-4">
                  <div className="w-18 h-18 bg-[#EBEBEB] rounded-full flex items-center justify-center">
                    <img src={image} alt="buildings-icon" className="h-12 w-12" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">{organization.name}</h2>
                    <Badge className="bg-[#ED8A09] text-white rounded-2xl px-3 py-2 mt-2 flex items-center gap-1">
                      <ShieldCheckered className="w-5 h-5" />
                      Administrator access
                    </Badge>
                  </div>
                </div>

                {/* Info Box */}
                <div className="flex flex-col sm:flex-row rounded-2xl bg-[#FEC89A33] text-sm text-gray-700 w-full lg:w-auto">
                  <div className="px-6 py-3 border-b sm:border-b-0 sm:border-r border-gray-200 text-center sm:text-left">
                    <span className="font-medium text-[#ED8A09] block">Your Role</span>
                    <span className="capitalize">{authState.user?.role}</span>
                  </div>
                  <div className="px-6 py-3 text-center items-center justify-center sm:justify-start gap-2">
                    <span className="font-medium text-[#ED8A09]">Created</span>
                    <span className=" flex items-center text-center gap-1">
                      <span className="text-center">
                        <Calendar size={16} />
                      </span>
                      <span>
                        {organization.created_at ? formatDate(organization.created_at) : 'Unknown'}
                      </span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Form Fields */}
              <Form {...form}>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                  {/* Organization Name and Website Row */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Organization Name */}
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem className="space-y-1">
                          <Label
                            htmlFor="orgName"
                            className="font-semibold text-lg flex items-center"
                          >
                            Organization Name *
                          </Label>
                          <div className="relative">
                            <Buildings className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <FormControl>
                              <Input
                                {...field}
                                id="orgName"
                                value={formData.organizationName}
                                placeholder="Enter organization name"
                                onChange={e => {
                                  field.onChange(e.target.value);
                                  handleFormDataChange('organizationName', e.target.value);
                                }}
                                className="pl-10 rounded-xl border 
                                  placeholder-shown:border-gray-300 
                                  focus:border-orange-300 
                                  not-placeholder-shown:border-orange-300 
                                  focus:outline-none focus:ring-0 focus-visible:ring-0"
                                disabled={isSubmitting || isUpdating}
                              />
                            </FormControl>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Company Website */}
                    <FormField
                      control={form.control}
                      name="website"
                      render={({ field }) => (
                        <FormItem className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <Label htmlFor="website" className="font-semibold text-lg">
                              Company Website
                            </Label>
                            <Badge className="bg-[#ED8A09] text-white text-xs rounded-2xl flex items-center gap-1">
                              <Sparkle className="h-3 w-3 text-white" /> AI Enhanced
                            </Badge>
                          </div>
                          <div className="relative">
                            <Globe className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <FormControl>
                              <Input
                                {...field}
                                id="website"
                                value={formData.website}
                                placeholder="https://your-company.com"
                                onChange={e => {
                                  field.onChange(e.target.value);
                                  handleFormDataChange('website', e.target.value);
                                }}
                                className="pl-10 rounded-xl border 
                                  placeholder-shown:border-gray-300 
                                  focus:border-orange-300 
                                  not-placeholder-shown:border-orange-300 
                                  focus:outline-none focus:ring-0 focus-visible:ring-0"
                                disabled={isSubmitting || isUpdating}
                              />
                            </FormControl>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  {/* Address Section */}
                  <div className="space-y-4">
                    <h4 className="font-semibold">Address Information</h4>

                    {/* Address Line 1 */}
                    <FormField
                      control={form.control}
                      name="address.line1"
                      render={({ field }) => (
                        <FormItem className="space-y-1">
                          <Label htmlFor="addressLine1" className="font-semibold">
                            Address Line 1 *
                          </Label>
                          <div className="relative">
                            <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <FormControl>
                              <Input
                                {...field}
                                id="addressLine1"
                                value={formData.addressLine1}
                                placeholder="Enter address line 1"
                                onChange={e => {
                                  field.onChange(e.target.value);
                                  handleFormDataChange('addressLine1', e.target.value);
                                }}
                                className="pl-10 rounded-xl border 
                                  placeholder-shown:border-gray-300 
                                  focus:border-orange-300 
                                  not-placeholder-shown:border-orange-300 
                                  focus:outline-none focus:ring-0 focus-visible:ring-0"
                                disabled={isSubmitting || isUpdating}
                              />
                            </FormControl>
                          </div>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    {/* Address Line 2 and Pincode Row */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Address Line 2 */}
                      <FormField
                        control={form.control}
                        name="address.line2"
                        render={({ field }) => (
                          <FormItem className="space-y-1">
                            <Label htmlFor="addressLine2" className="font-semibold">
                              Address Line 2
                            </Label>
                            <div className="relative">
                              <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                              <FormControl>
                                <Input
                                  {...field}
                                  id="addressLine2"
                                  value={formData.addressLine2}
                                  placeholder="Enter address line 2 (optional)"
                                  onChange={e => {
                                    field.onChange(e.target.value);
                                    handleFormDataChange('addressLine2', e.target.value);
                                  }}
                                  className="pl-10 rounded-xl border 
                                    placeholder-shown:border-gray-300 
                                    focus:border-orange-300 
                                    not-placeholder-shown:border-orange-300 
                                    focus:outline-none focus:ring-0 focus-visible:ring-0"
                                  disabled={isSubmitting || isUpdating}
                                />
                              </FormControl>
                            </div>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      {/* Pincode */}
                      <FormField
                        control={form.control}
                        name="address.pincode"
                        render={({ field }) => (
                          <FormItem className="space-y-1">
                            <Label htmlFor="pincode" className="font-semibold">
                              Pincode
                            </Label>
                            <div className="relative">
                              <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                              <FormControl>
                                <Input
                                  {...field}
                                  id="pincode"
                                  type="number"
                                  value={formData.pincode}
                                  placeholder="Enter pincode"
                                  onChange={e => {
                                    const value = e.target.value;
                                    field.onChange(value ? parseInt(value) : undefined);
                                    handleFormDataChange('pincode', value);
                                  }}
                                  className="pl-10 rounded-xl border 
                                    placeholder-shown:border-gray-300 
                                    focus:border-orange-300 
                                    not-placeholder-shown:border-orange-300 
                                    focus:outline-none focus:ring-0 focus-visible:ring-0"
                                  disabled={isSubmitting || isUpdating}
                                />
                              </FormControl>
                            </div>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>

                  {/* Contact Information */}
                  <div className="space-y-3">
                    <h4 className="font-semibold">Contact Information</h4>
                    <div className="flex flex-col md:flex-row items-center gap-4">
                      <FormField
                        control={form.control}
                        name="contact.email"
                        render={({ field }) => (
                          <FormItem className="w-full md:flex-1">
                            <div className="relative">
                              <Envelope className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                              <FormControl>
                                <Input
                                  {...field}
                                  value={formData.email}
                                  onChange={e => {
                                    field.onChange(e.target.value);
                                    handleFormDataChange('email', e.target.value);
                                  }}
                                  className="pl-10 rounded-xl border 
                                    placeholder-shown:border-gray-300 
                                    focus:border-orange-300 
                                    not-placeholder-shown:border-orange-300 
                                    focus:outline-none focus:ring-0 focus-visible:ring-0"
                                  placeholder="organization@example.com"
                                  disabled={isSubmitting || isUpdating}
                                />
                              </FormControl>
                            </div>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      <span className="text-sm  text-gray-400  md:block">or</span>
                      <FormField
                        control={form.control}
                        name="contact.phone"
                        render={({ field }) => (
                          <FormItem className="w-full md:flex-1">
                            <div className="relative">
                              <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                              <FormControl>
                                <Input
                                  {...field}
                                  placeholder="Phone Number"
                                  value={formData.phone}
                                  onChange={e => {
                                    field.onChange(e.target.value);
                                    handleFormDataChange('phone', e.target.value);
                                  }}
                                  className="pl-10 rounded-xl border 
                                    placeholder-shown:border-gray-300 
                                    focus:border-orange-300 
                                    not-placeholder-shown:border-orange-300 
                                    focus:outline-none focus:ring-0 focus-visible:ring-0"
                                  disabled={isSubmitting || isUpdating}
                                />
                              </FormControl>
                            </div>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col sm:flex-row gap-4 pt-4 justify-between">
                    <Button
                      type="button"
                      variant="outline"
                      className="px-6 py-2 text-sm order-2 sm:order-1"
                      onClick={() => navigate('/organization')}
                      disabled={isSubmitting || isUpdating}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      className="px-6 py-2 text-sm bg-black text-white order-1 sm:order-2"
                      disabled={isSubmitting || isUpdating}
                    >
                      {isSubmitting || isUpdating ? 'Saving...' : 'Save Changes'}
                    </Button>
                  </div>
                </form>
              </Form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
