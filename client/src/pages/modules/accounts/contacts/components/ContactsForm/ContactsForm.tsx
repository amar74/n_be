import React, { useState, useEffect } from 'react';
import { User, Mail, Phone } from 'lucide-react';
import { ContactCreate, ContactResponse, ContactUpdateRequest } from '@/types/accounts';

interface ContactsFormProps {
  onSubmit: (contact: ContactCreate) => Promise<any>;
  isLoading?: boolean;
  initialData?: ContactCreate;
  onCancel?: () => void;
  errors?: Record<string, string>;
}

export function ContactsForm({ 
  onSubmit, 
  isLoading = false, 
  initialData = {email: '', phone: '', name: '', title: ''}, 
  onCancel,
  errors = {},
}: ContactsFormProps) {
  const [formData, setFormData] = useState<ContactCreate>(initialData);

  useEffect(() => {
    setFormData({
      ...initialData,
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name?.trim() || !formData.email?.trim() || !formData.phone?.trim()) {
      return;
    }

    try {
      await onSubmit(formData);
      
      // Reset form if it's a create operation (no initial data)
      if (!initialData.name) {
        setFormData({email: '', phone: '', name: '', title: ''});
      }
    } catch (error) {
      // Error handling is done in the hook
    }
  };

  const handleChange = (field: keyof ContactResponse, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
      <div className="flex flex-col gap-6 w-full">
        {/* Header */}
        <div className="flex flex-col gap-2">
          <h2 className="font-inter font-bold text-[#0f0901] text-[24px] leading-normal flex items-center gap-2">
            <User className="h-6 w-6" />
            {initialData.name ? 'Edit Contact' : 'Add Secondary Contact'}
          </h2>
          <p className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
            {initialData.name ? 'Update contact details' : 'Add a new secondary contact for this account'}
          </p>
        </div>

        {/* Divider */}
        <div className="h-px w-full bg-[#e6e6e6]" />

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-6 w-full">
          {/* Row 1: Name + Role */}
          <div className="flex gap-4 w-full">
             <div className="w-[260px] flex flex-col gap-3">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
                Role *
              </label>
              <div className="relative">
              <input
                type="text"
                value={formData?.title || ''}
                onChange={(e) => handleChange('title', e.target.value)}
                placeholder="Enter title"
                className={`bg-white border ${errors.title ? 'border-red-500' : 'border-[#e6e6e6]'} w-full rounded-[14px] h-14 px-6 py-2 font-inter font-medium text-[#0f0901] text-[16px] focus:border-[#ff7b00] focus:outline-none`}
              />
              {errors.title && (
                <span className="text-red-500 text-sm mt-1">{errors.title}</span>
              )}
              </div>
            </div>
            {/* Name */}
            <div className="flex-1 flex flex-col gap-3">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
                Name *
              </label>
              <input
                type="text"
                value={formData?.name || ''}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="Enter contact name"
                className={`bg-white border ${errors.name ? 'border-red-500' : 'border-[#e6e6e6]'} rounded-[14px] h-14 px-6 py-2 font-inter font-medium text-[#0f0901] text-[16px] focus:border-[#ff7b00] focus:outline-none`}
              />
              {errors.name && (
                <span className="text-red-500 text-sm mt-1">{errors.name}</span>
              )}
            </div>
          </div> 

          {/* Row 2: Email + Phone */}
          <div className="flex gap-4 w-full">
            {/* Email */}
            <div className="flex-1 flex flex-col gap-3">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Email *
              </label>
              <input
                type="email"
                value={formData?.email || ''}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="Enter email address"
                required
                className={`bg-white border ${errors.email ? 'border-red-500' : 'border-[#e6e6e6]'} rounded-[14px] h-14 px-6 py-2 font-inter font-medium text-[#0f0901] text-[16px] focus:border-[#ff7b00] focus:outline-none`}
              />
              {errors.email && (
                <span className="text-red-500 text-sm mt-1">{errors.email}</span>
              )}
            </div>

            {/* Phone */}
            <div className="w-[280px] flex flex-col gap-3">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal flex items-center gap-2">
                <Phone className="h-4 w-4" />
                Phone *
              </label>
              <input
                type="tel"
                value={formData?.phone || ''}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder="(555) 123-4567"
                required
                className={`bg-white border ${errors.phone ? 'border-red-500' : 'border-[#e6e6e6]'} rounded-[14px] h-14 px-6 py-2 font-inter font-medium text-[#0f0901] text-[16px] focus:border-[#ff7b00] focus:outline-none`}
              />
              {errors.phone && (
                <span className="text-red-500 text-sm mt-1">{errors.phone}</span>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-4 pt-4">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={isLoading}
                className="bg-transparent border border-[#0f0901] rounded-[16px] h-14 flex items-center justify-center px-6 py-2 min-w-[120px]"
              >
                <span className="font-inter font-medium text-[#0f0901] text-[14px] leading-[24px]">
                  Cancel
                </span>
              </button>
            )}
            <button
              type="submit"
              disabled={isLoading || !formData.name?.trim() || !formData.email?.trim() || !formData.phone?.trim()}
              className="bg-[#0f0901] rounded-[16px] h-14 flex items-center justify-center px-8 py-2 min-w-[160px] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="font-inter font-medium text-white text-[14px] leading-[24px]">
                {isLoading ? 'Saving...' : initialData.name ? 'Update Contact' : 'Add Contact'}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
