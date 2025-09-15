import { AccountCreate } from '@/types/accounts';

export enum ClientType {
  TIER_1 = 'tier_1',
  TIER_2 = 'tier_2',
  TIER_3 = 'tier_3'
}

export interface CreateAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AccountCreate) => void;
  isLoading?: boolean;
}

export interface UseCreateAccountModalReturn {
  formData: AccountCreate;
  errors: Record<string, string>;
  isSubmitting: boolean;
  handleInputChange: (field: keyof AccountCreate, value: string | object) => void;
  handleSubmit: (e: React.FormEvent) => void;
  handleClose: () => void;
  resetForm: () => void;
}
