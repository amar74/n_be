export interface Contact {
  id: string;
  name: string;
  role: string;
  email: string;
  phone: string;
  status: 'primary' | 'secondary';
  accountId: string;
  createdAt: string;
  updatedAt: string;
}

export interface ContactFormData {
  name: string;
  role: string;
  email: string;
  phone: string;
}

export interface ContactRole {
  value: string;
  label: string;
}

export interface ContactsTabProps {
  accountId: string;
}

export interface ContactsFormProps {
  onSubmit: (contact: ContactFormData) => Promise<any>;
  isLoading?: boolean;
  initialData?: Partial<ContactFormData>;
  onCancel?: () => void;
  defaultFormValues: ContactFormData;
}

export interface ContactsListProps {
  contacts: Contact[];
  onEdit: (contact: Contact) => void;
  onDelete: (contactId: string) => void;
  isLoading?: boolean;
}

export interface EditContactModalProps {
  isOpen: boolean;
  contact: Contact | null;
  onClose: () => void;
  onSave: (contactId: string, data: ContactFormData) => Promise<any>;
  isLoading?: boolean;
}
