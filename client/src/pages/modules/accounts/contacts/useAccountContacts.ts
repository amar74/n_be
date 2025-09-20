import { useState, useMemo } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Contact, ContactFormData } from './ContactsTab.types';
import { MOCK_CONTACTS, DEFAULT_CONTACT_FORM_VALUES } from './ContactsTab.constants';

export function useAccountContacts(accountId: string) {
  const { toast } = useToast();
  
  // State
  const [contacts, setContacts] = useState<Contact[]>(MOCK_CONTACTS);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);

  // Computed values
  const primaryContact = useMemo(() => {
    return contacts.find(contact => contact.status === 'primary');
  }, [contacts]);

  const secondaryContacts = useMemo(() => {
    return contacts.filter(contact => contact.status === 'secondary')
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  }, [contacts]);

  const allContacts = useMemo(() => {
    return [...contacts].sort((a, b) => {
      // Primary contact first, then by most recent update
      if (a.status === 'primary' && b.status !== 'primary') return -1;
      if (b.status === 'primary' && a.status !== 'primary') return 1;
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });
  }, [contacts]);

  // Actions
  const createContact = async (contactData: ContactFormData) => {
    setIsCreating(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newContact: Contact = {
        id: Date.now().toString(),
        ...contactData,
        status: 'secondary', // New contacts are always secondary
        accountId,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      setContacts(prev => [newContact, ...prev]);
      
      toast({
        title: '✅ Contact Added',
        description: 'New contact has been successfully added.',
      });
      
      return newContact;
    } catch (error) {
      console.error('Error creating contact:', error);
      toast({
        title: 'Error',
        description: 'Failed to add contact. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsCreating(false);
    }
  };

  const updateContact = async (contactId: string, contactData: ContactFormData) => {
    setIsUpdating(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setContacts(prev => prev.map(contact => 
        contact.id === contactId 
          ? { ...contact, ...contactData, updatedAt: new Date().toISOString() }
          : contact
      ));
      
      toast({
        title: '✅ Contact Updated',
        description: 'Contact information has been successfully updated.',
      });
    } catch (error) {
      console.error('Error updating contact:', error);
      toast({
        title: 'Error',
        description: 'Failed to update contact. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsUpdating(false);
    }
  };

  const deleteContact = async (contactId: string) => {
    const contactToDelete = contacts.find(c => c.id === contactId);
    
    // Prevent deleting primary contact
    if (contactToDelete?.status === 'primary') {
      toast({
        title: 'Cannot Delete Primary Contact',
        description: 'Primary contact cannot be deleted. Please assign a new primary contact first.',
        variant: 'destructive',
      });
      return;
    }

    setIsDeleting(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setContacts(prev => prev.filter(contact => contact.id !== contactId));
      
      toast({
        title: '✅ Contact Deleted',
        description: 'Contact has been successfully removed.',
      });
    } catch (error) {
      console.error('Error deleting contact:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete contact. Please try again.',
        variant: 'destructive',
      });
      throw error;
    } finally {
      setIsDeleting(false);
    }
  };

  const startEditContact = (contact: Contact) => {
    setEditingContact(contact);
    setShowEditModal(true);
  };

  const cancelEdit = () => {
    setEditingContact(null);
    setShowEditModal(false);
  };

  const saveEdit = async (contactId: string, data: ContactFormData) => {
    await updateContact(contactId, data);
    setEditingContact(null);
    setShowEditModal(false);
  };

  return {
    // Data
    contacts: allContacts,
    primaryContact,
    secondaryContacts,
    editingContact,
    showEditModal,
    
    // State
    isLoading,
    isCreating,
    isUpdating,
    isDeleting,
    
    // Actions
    createContact,
    updateContact,
    deleteContact,
    startEditContact,
    cancelEdit,
    saveEdit,
    
    // Default values for forms
    defaultFormValues: DEFAULT_CONTACT_FORM_VALUES,
  };
}
