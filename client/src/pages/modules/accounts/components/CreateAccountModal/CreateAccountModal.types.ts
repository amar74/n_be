import { AccountCreate } from '@/types/accounts';

export enum ClientType {
  TIER_1 = 'tier_1',
  TIER_2 = 'tier_2',
  TIER_3 = 'tier_3'
}

// UI-specific address interface that includes state field for form handling
export interface UIAddressData {
  line1: string;
  line2: string | null;
  city: string | null;
  state: string | null; // UI-only field for state dropdown
  pincode: number | null;
}

// UI-specific form data that includes state field
export interface UIAccountFormData {
  client_name: string;
  company_website?: string | null;
  client_address: UIAddressData;
  primary_contact: {
    name: string;
    email: string;
    phone: string;
    title?: string | null;
  };
  secondary_contacts?: Array<{
    name: string;
    email: string;
    phone: string;
    title?: string | null;
  }>;
  client_type: 'tier_1' | 'tier_2' | 'tier_3';
  market_sector?: string | null;
  notes?: string | null;
}

export interface CreateAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AccountCreate) => void;
  isLoading?: boolean;
  errors?: Record<string, string>;
}

export interface UseCreateAccountModalReturn {
  formData: UIAccountFormData;
  errors: Record<string, string>;
  isSubmitting: boolean;
  isAnalyzing: boolean;
  showAISuggestions: boolean;
  handleInputChange: (field: string, value: string | object) => void;
  handleAddressChange: (field: keyof UIAddressData, value: string | number | null) => void;
  handlePlaceSelect: (value: string, placeDetails?: google.maps.places.PlaceResult) => void;
  handleWebsiteChange: (value: string) => void;
  handleSubmit: (e: React.FormEvent) => void;
  handleClose: () => void;
  resetForm: () => void;
}
