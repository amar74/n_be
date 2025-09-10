import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Buildings, EnvelopeSimple, Phone, MapPin, Globe, Sparkle } from 'phosphor-react';
import Header2 from './Header2';

export default function CreateOrganization() {
  const [formData, setFormData] = useState({
    website: '',
    organizationName: '',
    address: '',
    email: '',
    phone: ''
  });

  return (
    <div className="bg-[#F5F3F2] flex flex-col min-h-screen">
      {/* Header */}
      <Header2 />

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center px-6 py-4 pt-2 ">
        {/* Title Section */}
        <div className="text-center mb-3 max-w-xl">
          <h1 className="text-2xl font-bold text-orange-500 mb-2">
            Create Your Organization
          </h1>
          <p className="text-gray-600 text-sm">
            Set up your organization to get started with the platform. You need an organization to access all features and
            collaborate with your team.
          </p>
        </div>

        {/* Form Field */}
        <div className="w-full max-w-3xl p-6 rounded-3xl bg-white shadow-md">
          {/* Progress Indicator */}
          <div className="flex items-center justify-center gap-4 mb-8">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium bg-orange-500 text-white">
                1
              </div>
              <span className="text-sm font-medium">Organization Setup</span>
            </div>
            <div className="w-8 h-px bg-[#A7A7A7]"></div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium bg-gray-200 text-gray-500">
                2
              </div>
              <span className="text-sm font-medium text-[#A7A7A7]">Platform Access</span>
            </div>
          </div>

          {/* Organization Details Section */}
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900 mb-1">Organization Details</h2>
              <p className="text-xs text-[#A7A7A7] pb-2 border-b border-[#A7A7A7]">
                Provide information about your organization. Our AI will help auto-complete field where possible.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Company Website */}
              <div className="space-y-2">
                <div className="flex items-center">
                  <Label htmlFor="website" className="text-sm font-medium mr-4">
                    Company Website
                  </Label>
                  <Badge
                    variant="secondary"
                    className="bg-[#ED8A09] text-white text-xs px-3 py-0 rounded-2xl flex items-center gap-1"
                  >
                    <Sparkle className="h-3 w-3 text-white" /> AI Enhanced
                  </Badge>
                </div>
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="website"
                    value={formData.website}
                    onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                    placeholder="https://your-company.com"
                    className="pl-10 mt-2 border 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-300 
                      not-placeholder-shown:border-orange-300 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                  />
                </div>
              </div>

              {/* Organization Name */}
              <div className="space-y-2">
                <div className="flex items-center">
                  <Label htmlFor="organizationName" className="text-sm font-medium">
                    Organization Name *
                  </Label>
                  <span className="ml-4 text-xs invisible">placeholder</span>
                </div>
                <div className="relative">
                  <Buildings className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    id="organizationName"
                    value={formData.organizationName}
                    onChange={(e) => setFormData({ ...formData, organizationName: e.target.value })}
                    placeholder="Enter Company Name"
                    className="pl-10 mt-2 border 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-300 
                      not-placeholder-shown:border-orange-300 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                  />
                </div>
              </div>
            </div>

            {/* Address */}
            <div className="space-y-2">
              <Label htmlFor="address" className="text-sm font-medium">
                Address
              </Label>
              <div className="relative">
                <MapPin className="absolute left-2 top-3 h-4 w-4 text-gray-400" />
                <textarea
                  id="address"
                  rows={2}
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Enter Company Address"
                  className="w-full pl-8 pr-2 py-2 border 
                    placeholder-shown:border-gray-300 
                    focus:border-orange-300 
                    not-placeholder-shown:border-orange-300 
                    bg-gray-100 rounded-md resize-none 
                    focus:outline-none focus:ring-0 focus-visible:ring-0"
                />
              </div>
            </div>

            {/* Contact Information */}
            <div>
              <h3 className="font-semibold mb-2">Contact Information</h3>
              <div className="flex items-center gap-4">
                <div className="relative flex-1">
                  <EnvelopeSimple className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="johndoe46@gmail.com"
                    className="pl-10 border 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-300 
                      not-placeholder-shown:border-orange-300 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                  />
                </div>
                <span className="text-sm text-gray-500">or</span>
                <div className="relative flex-1">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="Phone Number"
                    className="pl-10 border 
                      placeholder-shown:border-gray-300 
                      focus:border-orange-300 
                      not-placeholder-shown:border-orange-300 
                      focus:outline-none focus:ring-0 focus-visible:ring-0"
                  />
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-6 pt-2 justify-between">
              <Button variant="outline" className=" py-2 text-sm mx-2">
                Back to Sign-In
              </Button>
              <Button className=" py-2 mx-2 text-sm bg-black text-white">
                Create Organization
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
