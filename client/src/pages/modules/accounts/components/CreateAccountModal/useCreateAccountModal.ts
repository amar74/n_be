import { useState, useCallback } from 'react';
import { CreateAccountFormData, validateForm } from './CreateAccountModal.schema';
import { INITIAL_FORM_DATA } from './CreateAccountModal.constants';
import { UseCreateAccountModalReturn } from './CreateAccountModal.types';

export function useCreateAccountModal(
  onSubmit: (data: CreateAccountFormData) => void,
  onClose: () => void
): UseCreateAccountModalReturn {
  const [formData, setFormData] = useState<CreateAccountFormData>(INITIAL_FORM_DATA);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = useCallback((field: keyof CreateAccountFormData, value: string) => {
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
      resetForm();
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
