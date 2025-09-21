import { useState, useCallback, useEffect } from 'react';
import { validateForm } from './CreateAccountModal.schema';
import { INITIAL_FORM_DATA } from './CreateAccountModal.constants';
import { UseCreateAccountModalReturn } from './CreateAccountModal.types';
import { AccountCreate } from '@/types/accounts';

export function useCreateAccountModal(
  onSubmit: (data: AccountCreate) => void,
  onClose: () => void,
  backendErrors: Record<string, string> = {}
): UseCreateAccountModalReturn {
  const [formData, setFormData] = useState<AccountCreate>(INITIAL_FORM_DATA);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = useCallback((field: keyof AccountCreate, value: string | object) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear errors when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  }, [validationErrors]);

  const resetForm = useCallback(() => {
    setFormData(INITIAL_FORM_DATA);
    setValidationErrors({});
    setIsSubmitting(false);
  }, []);

  const handleClose = useCallback(() => {
    resetForm();
    onClose();
  }, [resetForm, onClose]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const newValidationErrors = validateForm(formData);
    
    if (Object.keys(newValidationErrors).length > 0) {
      setValidationErrors(newValidationErrors);
      return;
    }

    setIsSubmitting(true);
    
    try {
      await onSubmit(formData);
      // resetForm();
    } catch (error) {
      console.error('Form submission error:', error);
      // Handle submission error if needed
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, onSubmit, resetForm]);

  // Handle backend errors
  useEffect(() => {
    if (Object.keys(backendErrors).length > 0) {
      setValidationErrors(backendErrors);
    }
  }, [backendErrors]);

  // Combine validation and backend errors
  const errors = { ...validationErrors };

  return {
    formData,
    errors,
    isSubmitting,
    handleInputChange,
    handleSubmit,
    handleClose,
    resetForm,
  };
}
