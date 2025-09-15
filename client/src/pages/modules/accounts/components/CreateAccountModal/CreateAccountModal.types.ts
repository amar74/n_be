import { CreateAccountFormData } from './CreateAccountModal.schema';

export interface CreateAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateAccountFormData) => void;
  isLoading?: boolean;
}

export interface UseCreateAccountModalReturn {
  formData: CreateAccountFormData;
  errors: Record<string, string>;
  isSubmitting: boolean;
  handleInputChange: (field: keyof CreateAccountFormData, value: string) => void;
  handleSubmit: (e: React.FormEvent) => void;
  handleClose: () => void;
  resetForm: () => void;
}

export { CreateAccountFormData };
