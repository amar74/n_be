import { useState } from 'react';
import { useAccountContacts } from '@/hooks/useAccountContacts';
import { ContactCreate, ContactResponse, ContactUpdateRequest } from '@/types/accounts';

export function useContacts(accountId: string) {
  const {
    contactsData, 
    addContact, deleteContact, updateContact,
    isAddingContact, isContactsLoading, isDeletingContact, isUpdatingContact
   } = useAccountContacts(accountId)
  const contacts = contactsData?.contacts || [];
  // State

  const [editingContact, setEditingContact] = useState<ContactResponse | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);


  // Actions
  const createContact = async (contactData: ContactCreate) => {
    addContact({accountId, contact: {contact: contactData}})
  };

  const handleUpdateContact = async (contactId: string, contactData: ContactUpdateRequest) => {
    updateContact({accountId, contactId, contact: contactData})
  };

  const handleDeleteContact = async (contactId: string) => {      
    deleteContact({accountId, contactId})
  };

  const startEditContact = (contact: ContactResponse) => {
    setEditingContact(contact);
    setShowEditModal(true);
  };

  const cancelEdit = () => {
    setEditingContact(null);
    setShowEditModal(false);
  };

  const saveEdit = async (contactId: string, data: ContactUpdateRequest) => {
    await handleUpdateContact(contactId, data);
    setEditingContact(null);
    setShowEditModal(false);
  };

  return {
    // Data
    contacts,
    editingContact,
    showEditModal,
    
    // State
    isContactsLoading,
    isAddingContact,
    isUpdatingContact,
    isDeletingContact,
    
    // Actions
    createContact,
    updateContact: handleUpdateContact,
    deleteContact: handleDeleteContact,
    startEditContact,
    cancelEdit,
    saveEdit,
  };
}
