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
    
    // Actions
    createContact,
    startEditContact,
    cancelEdit,
    saveEdit,
    deleteContact,
  } = useContacts(accountId);

  return (
    <div className="flex flex-col gap-8 w-full">
      {/* Add Contact Form */}
      <ContactsForm
        onSubmit={createContact}
        isLoading={isCreating}
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
