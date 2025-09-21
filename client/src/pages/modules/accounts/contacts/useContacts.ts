import { useEffect, useState } from 'react';
import { useAccountContacts } from '@/hooks/useAccountContacts';
import { ContactCreate, ContactResponse, ContactUpdateRequest } from '@/types/accounts';
import { AxiosError } from 'axios';
import { parseBackendErrors } from '@/utils/errorParser';
import { HTTPValidationError } from '@/types/validationError';

export function useContacts(accountId: string) {
  const {
    contactsData, 
    addContact, deleteContact, updateContact,
    isAddingContact, isContactsLoading, isDeletingContact, isUpdatingContact,
    addContactError, updateContactError, deleteContactError,
    addContactSuccess, updateContactSuccess, deleteContactSuccess,
   } = useAccountContacts(accountId)
  const contacts = contactsData?.contacts || [];
  // State
  const [createErrors, setCreateErrors] = useState<Record<string, string>>({});
  const [updateErrors, setUpdateErrors] = useState<Record<string, string>>();
  const [editingContact, setEditingContact] = useState<ContactResponse | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);


  // Actions
  const createContact = async (contactData: ContactCreate) => {
    await addContact({accountId, contact: {contact: contactData}});
  };

  const handleUpdateContact = async (contactId: string, contactData: ContactUpdateRequest) => {
    await updateContact({accountId, contactId, contact: contactData});
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


  // Handle create errors
  useEffect(() => {
    if (addContactError && (addContactError as AxiosError)?.response?.data) {
      const errors = parseBackendErrors((addContactError as AxiosError).response?.data as HTTPValidationError, ['name', 'email', 'phone', 'title']);
      setCreateErrors(errors);
    } else {
      setCreateErrors({});
    }
  }, [addContactError]);

  // Handle update errors
  useEffect(() => {
    console.log(updateContactError);
    
    if (updateContactError && (updateContactError as AxiosError)?.response?.data) {
      const errors = parseBackendErrors((updateContactError as AxiosError).response?.data as HTTPValidationError, ['name', 'email', 'phone', 'title']);
      setUpdateErrors(errors);
    } else {
      setUpdateErrors({});
    }
  }, [updateContactError]);

  // Clear errors on success
  useEffect(() => {
    if (addContactSuccess) {
      setCreateErrors({});
    }
  }, [addContactSuccess]);

  useEffect(() => {
    if (updateContactSuccess) {
      setEditingContact(null);
      setShowEditModal(false);
      setUpdateErrors({});
    }
  }, [updateContactSuccess]);

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
    createErrors,
    updateErrors,
    
    // Actions
    createContact,
    updateContact: handleUpdateContact,
    deleteContact: handleDeleteContact,
    startEditContact,
    cancelEdit,
  };
}
