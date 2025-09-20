import React from 'react';
import { ContactsForm } from './components/ContactsForm';
import { ContactsList } from './components/ContactsList';
import { EditContactModal } from './components/EditContactModal';
import { useAccountContacts } from './useAccountContacts';
import { ContactsTabProps } from './ContactsTab.types';

export function ContactsTab({ accountId }: ContactsTabProps) {
  const {
    // Data
    contacts,
    editingContact,
    showEditModal,
    defaultFormValues,
    
    // State
    isLoading,
    isCreating,
    isUpdating,
    isDeleting,
    
    // Actions
    createContact,
    startEditContact,
    cancelEdit,
    saveEdit,
    deleteContact,
  } = useAccountContacts(accountId);

  return (
    <div className="flex flex-col gap-8 w-full">
      {/* Add Contact Form */}
      <ContactsForm
        onSubmit={createContact}
        isLoading={isCreating}
        defaultFormValues={defaultFormValues}
      />

      {/* Contacts List */}
      <ContactsList
        contacts={contacts}
        onEdit={startEditContact}
        onDelete={deleteContact}
        isLoading={isLoading}
      />

      {/* Edit Modal */}
      <EditContactModal
        isOpen={showEditModal}
        contact={editingContact}
        onClose={cancelEdit}
        onSave={saveEdit}
        isLoading={isUpdating}
      />
    </div>
  );
}
