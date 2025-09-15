import { useState, useCallback } from 'react';
import { validateForm } from './CreateAccountModal.schema';
import { INITIAL_FORM_DATA } from './CreateAccountModal.constants';
import { UseCreateAccountModalReturn } from './CreateAccountModal.types';
import { AccountCreate } from '@/types/accounts';

export function useCreateAccountModal(
  onSubmit: (data: AccountCreate) => void,
  onClose: () => void
): UseCreateAccountModalReturn {
  const [formData, setFormData] = useState<AccountCreate>(INITIAL_FORM_DATA);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = useCallback((field: keyof AccountCreate, value: string | object) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  }, [errors]);

  const resetForm = useCallback(() => {
    setFormData(INITIAL_FORM_DATA);
    setErrors({});
    setIsSubmitting(false);
  }, []);

  const handleClose = useCallback(() => {
    resetForm();
    onClose();
  }, [resetForm, onClose]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const validationErrors = validateForm(formData);
    
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
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
