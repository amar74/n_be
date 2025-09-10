import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Header2 from './Header2';
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
  ShieldCheckered
} from 'phosphor-react';
import image from '@/assets/image.png';

export default function OrganizationDetailsView() {
  return (
    <div className="min-h-screen bg-[#F5F3F2]">
      {/* Header */}
      <Header2 />

      {/* Main Content */}
      <main className="p-2">
        <div className="max-w-5xl mx-auto px-4 md:px-20">
          {/* Breadcrumb just above card */}
          <div className="text-sm text-gray-500 mb-3 flex flex-wrap gap-1 items-center">
            <House size={18} className="text-gray-700" />
            <CaretRight size={16} className="text-gray-700" />
            Profile
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
                    <h2 className="text-2xl font-bold break-words">
                      Jai Laxmi Narayan Seva Trust
                    </h2>
                    <Badge className="bg-green-100 text-[#0C8102] mt-2 rounded-xl flex items-center gap-2">
                      <span className="rounded-full w-3 h-3 bg-[#0C8102]"></span>
                      <span className="text-sm">Active Organization</span>
                    </Badge>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="rounded-full bg-gray-50 hover:bg-gray-100"
                  >
                    <PencilSimpleLine className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="rounded-full bg-gray-50 hover:bg-gray-100"
                  >
                    <DotsThreeVertical className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {/* Admin + Created On */}
              <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-2">
                <Badge className="bg-[#ED8A091A] text-[#ED8A09] rounded-2xl px-3 py-2 flex items-center gap-1">
                  <ShieldCheckered className="w-4 h-4" />
                  Administrator
                </Badge>
                <div className="flex flex-row gap-2 items-center text-sm">
                  <span className="text-gray-500 text-sm font-semibold">Created on</span>
                  <Calendar className="w-4 h-4" />
                  <span className="font-medium">August 24, 2025</span>
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
                      <a
                        href="https://your-company.com"
                        className="hover:underline text-blue-600 break-words"
                      >
                        https://your-company.com
                      </a>
                    </div>
                  </div>

                  <div className="border-b border-gray-200 pb-2">
                    <h3 className="font-semibold mb-2">Organization Address</h3>
                    <div className="flex items-start gap-2 text-gray-600">
                      <MapPin className="w-4 h-4 mt-1" />
                      <span>
                        826, Laxmi Deep Building, District Center,
                        <br />
                        Laxmi Nagar, Delhi
                      </span>
                    </div>
                  </div>

                  <div className="border-b border-gray-200 pb-2">
                    <h3 className="font-semibold mb-2">Contact Information</h3>
                    <div className="flex items-center gap-2 text-gray-600">
                      <PhoneCall className="w-4 h-4" />
                      <span>+91 9871707584</span>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold mb-2">Last Updated</h3>
                    <div className="flex items-center gap-2 text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>August 24, 2025</span>
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
                    >
                      <UserCircle className="w-4 h-4 mr-2" />
                      View Accounts
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start rounded-xl px-4 py-3 text-gray-700 hover:text-orange-500 hover:bg-gray-100"
                    >
                      <ChartLineUp className="w-4 h-4 mr-2" />
                      View Reports
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start rounded-xl px-4 py-3 text-gray-700 hover:text-orange-500 hover:bg-gray-100"
                    >
                      <Gear className="w-4 h-4 mr-2" />
                      Manage Setting
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
