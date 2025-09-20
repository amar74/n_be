import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ContactsForm } from '../ContactsForm';
import { ContactResponse, ContactUpdateRequest } from '@/types/accounts';

interface EditContactModalProps {
  isOpen: boolean;
  contact: ContactResponse | null;
  onClose: () => void;
  onSave: (contactId: string, data: ContactUpdateRequest) => Promise<any>;
  isLoading?: boolean;
}

export function EditContactModal({ 
  isOpen, 
  contact, 
  onClose, 
  onSave, 
  isLoading = false 
}: EditContactModalProps) {
  const handleSubmit = async (formData: ContactUpdateRequest) => {
    if (!contact) return;
    
    await onSave(contact.contact_id, formData);
    onClose();
  };

  if (!contact) return null;

  const initialData = {
    name: contact.name,
    title: contact.title,
    email: contact.email,
    phone: contact.phone,
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[800px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="font-inter font-bold text-[#0f0901] text-[20px]">
            Edit Contact
          </DialogTitle>
          <DialogDescription className="font-inter font-medium text-[#a7a7a7] text-[16px]">
            Update contact information below.
          </DialogDescription>
        </DialogHeader>
        
        <div className="mt-4">
          <ContactsForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            initialData={initialData}
            onCancel={onClose}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
