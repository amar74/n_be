import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ContactsForm } from '../ContactsForm';
import { Contact, ContactFormData } from '../../ContactsTab.types';
import { DEFAULT_CONTACT_FORM_VALUES } from '../../ContactsTab.constants';

interface EditContactModalProps {
  isOpen: boolean;
  contact: Contact | null;
  onClose: () => void;
  onSave: (contactId: string, data: ContactFormData) => Promise<any>;
  isLoading?: boolean;
}

export function EditContactModal({ 
  isOpen, 
  contact, 
  onClose, 
  onSave, 
  isLoading = false 
}: EditContactModalProps) {
  const handleSubmit = async (formData: ContactFormData) => {
    if (!contact) return;
    
    await onSave(contact.id, formData);
    onClose();
  };

  if (!contact) return null;

  const initialData = {
    name: contact.name,
    role: contact.role,
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
            defaultFormValues={DEFAULT_CONTACT_FORM_VALUES}
          />
        </div>
      </DialogContent>
    </Dialog>
  );
}
