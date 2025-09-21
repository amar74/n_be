import React, { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X, Sparkles } from 'lucide-react';
import { CreateAccountModalProps } from './CreateAccountModal.types';
import { useCreateAccountModal } from './useCreateAccountModal';
import { CompanyWebsiteForm } from './components/CompanyWebsiteForm';
import { AddressForm } from './components/AddressForm';
import { ContactForm } from './components/ContactForm';
import { BusinessForm } from './components/BusinessForm';

export function CreateAccountModal({ isOpen, onClose, onSubmit, isLoading = false, errors: backendErrors = {} }: CreateAccountModalProps) {
  const {
    formData,
    errors,
    isSubmitting,
    isAnalyzing,
    showAISuggestions,
    handleInputChange,
    handleAddressChange,
    handlePlaceSelect,
    handleWebsiteChange,
    handleSubmit,
    handleClose,
  } = useCreateAccountModal(onSubmit, onClose, backendErrors);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, handleClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={handleClose}
      >
          {/* Modal */}
          <div 
            className="bg-white rounded-[36px] shadow-[0px_4px_12px_0px_rgba(191,191,191,0.48)] w-full max-w-4xl max-h-[92vh] flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
          {/* Fixed Header */}
          <div className="px-8 py-6 border-b border-gray-300 flex-shrink-0">
            <div className="flex items-start justify-between">
              <div className="flex flex-col gap-4">
                <h2 className="text-2xl font-semibold text-[#ED8A09]">
                  Create New Account
                </h2>
                <p className="text-gray-500">
                  Add a new client account to your portfolio
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleClose}
                className="h-8 w-8 p-0 hover:bg-gray-100"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>

          {/* Scrollable Form Container */}
          <div className="flex-1 overflow-y-auto px-8 py-6 custom-scrollbar">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 sm:gap-6">
              {/* Company Website Section */}
              <CompanyWebsiteForm 
                value={formData.company_website || ''}
                onChange={handleWebsiteChange}
                isAnalyzing={isAnalyzing}
                showAISuggestions={showAISuggestions}
                error={errors['company_website']}
              />

              {/* Address and Client Info */}
              <AddressForm 
                formData={formData}
                errors={errors}
                onChange={handleInputChange}
                onAddressChange={handleAddressChange}
                onPlaceSelect={handlePlaceSelect}
                showAISuggestions={showAISuggestions}
              />

              {/* Contact Fields */}
              <ContactForm 
                formData={formData}
                errors={errors}
                onChange={handleInputChange}
              />

              {/* Business Information */}
              <BusinessForm 
                formData={formData}
                errors={errors}
                onChange={handleInputChange}
              />

              {/* AI Suggestions Info */}
              {showAISuggestions && (
                <div className="bg-purple-50 border border-purple-200 rounded-md p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="h-4 w-4 text-purple-600" />
                    <span className="text-sm font-medium text-purple-900">AI Suggestions Applied</span>
                  </div>
                  <p className="text-xs text-purple-700">
                    We've automatically filled in some fields based on your website. Please review and adjust as needed.
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 pt-2 justify-between">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  className="px-6 py-2 text-sm order-2 sm:order-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting || isLoading}
                  className="px-6 py-2 text-sm bg-black text-white order-1 sm:order-2"
                >
                  {isSubmitting || isLoading ? 'Creating...' : 'Create Account'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Custom Scrollbar Styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
          .custom-scrollbar::-webkit-scrollbar {
            width: 6px;
          }
          .custom-scrollbar::-webkit-scrollbar-track {
            background: #f3f3f3;
            border-radius: 3px;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #ed8a09;
            border-radius: 3px;
          }
          .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: #d97706;
          }
          .custom-scrollbar {
            scrollbar-width: thin;
            scrollbar-color: #ed8a09 #f3f3f3;
          }
        `
      }} />
    </>
  );
}