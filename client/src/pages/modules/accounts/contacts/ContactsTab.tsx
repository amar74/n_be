import { ContactsForm } from './components/ContactsForm';
import { ContactsList } from './components/ContactsList';
import { EditContactModal } from './components/EditContactModal';
import { useContacts } from './useContacts';

export interface ContactsTabProps {
  accountId: string;
}

export function ContactsTab({ accountId }: ContactsTabProps) {
  const {
    // Data
    contacts,
    editingContact,
    showEditModal,
    
    // State
    isContactsLoading: isLoading,
    isAddingContact: isCreating,
    isUpdatingContact: isUpdating,
    isDeletingContact: isDeleting,
    createErrors,
    updateErrors,
    
    // Actions
    createContact,
    startEditContact,
    cancelEdit,
    updateContact,
    deleteContact,
  } = useContacts(accountId);

  return (
    <div className="flex flex-col gap-8 w-full">
      {/* Add Contact Form */}
      <ContactsForm
        onSubmit={createContact}
        isLoading={isCreating}
        errors={createErrors}
      />

      {/* Contacts List */}
      <ContactsList
        accountId={accountId}
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
        onSave={updateContact}
        isLoading={isUpdating}
        errors={updateErrors}
      />
    </div>
  );
}
