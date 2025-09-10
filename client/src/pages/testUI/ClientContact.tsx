import React from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

const ClientContact: React.FC = () => {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-4">
      {/* Header */}
      <div className="mb-4 border-b border-gray-200 pb-4">
        <h2 className="text-lg font-bold text-gray-900">Client Contact</h2>
        <p className="text-sm font-semibold text-gray-500">
          Manage client contact information
        </p>
      </div>

      {/* Contact Row */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center gap-3 border border-gray-200 rounded-2xl px-6 pt-6 pb-2">
        {/* Name */}
        <div className="flex flex-col w-full lg:w-1/5">
          <Label className="text-sm text-gray-500 mb-1">Name</Label>
          <input
            type="text"
            placeholder="David Rodriguez"
            className="w-full bg-gray-50 px-4 py-2 rounded-lg border border-gray-200 text-gray-900 font-semibold outline-none focus:border-[#FF7B00]"
          />
        </div>

        {/* Role */}
        <div className="flex flex-col w-full lg:w-1/5">
          <Label className="text-sm text-gray-500 mb-1">Role</Label>
          <input
            type="text"
            placeholder="Primary Contact"
            className="w-full bg-gray-50 px-4 py-2 rounded-lg border border-gray-200 text-gray-900 font-semibold outline-none focus:border-[#FF7B00]"
          />
        </div>

        {/* Email */}
        <div className="flex flex-col w-full lg:w-1/4">
          <Label className="text-sm text-gray-500 mb-1">E-Mail</Label>
          <input
            type="email"
            placeholder="david.rodriguez@losangelescompany.com"
            className="w-full bg-gray-50 px-4 py-2 rounded-lg border border-gray-200 text-gray-900 font-medium truncate outline-none focus:border-[#FF7B00]"
          />
        </div>

        {/* Phone */}
        <div className="flex flex-col w-full lg:w-1/5">
          <Label className="text-sm text-gray-500 mb-1">Phone</Label>
          <input
            type="text"
            placeholder="(555) 123-4567"
            className="w-full bg-gray-50 px-4 py-2 rounded-lg border border-gray-200 text-gray-900 font-semibold outline-none focus:border-[#FF7B00] "
          />
        </div>

        {/* Primary Badge */}
        <div className="flex w-full lg:w-auto items-center">
          <Button className="bg-[#ED8A09] text-white rounded-lg px-8 text-sm font-medium mt-6">
            Primary
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ClientContact;
