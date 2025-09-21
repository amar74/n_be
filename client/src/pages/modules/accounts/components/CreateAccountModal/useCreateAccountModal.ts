import { useState, useCallback, useEffect } from 'react';
import { validateForm } from './CreateAccountModal.schema';
import { INITIAL_FORM_DATA, US_STATES } from './CreateAccountModal.constants';
import { UseCreateAccountModalReturn, UIAccountFormData, UIAddressData } from './CreateAccountModal.types';
import { AccountCreate } from '@/types/accounts';

export function useCreateAccountModal(
  onSubmit: (data: AccountCreate) => void,
  onClose: () => void,
  backendErrors: Record<string, string> = {}
): UseCreateAccountModalReturn {
  const [formData, setFormData] = useState<UIAccountFormData>(INITIAL_FORM_DATA);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = useCallback((field: string, value: string | object) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear errors when user starts typing
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: '' }));
    }
  }, [validationErrors]);

  const handleAddressChange = useCallback((field: keyof UIAddressData, value: string | number | null) => {
    setFormData(prev => ({
      ...prev,
      client_address: {
        ...prev.client_address,
        [field]: value,
      }
    }));
    
    // Clear errors when user starts typing
    const errorKey = `client_address.${field}`;
    if (validationErrors[errorKey]) {
      setValidationErrors(prev => ({ ...prev, [errorKey]: '' }));
    }
  }, [validationErrors]);

  const handlePlaceSelect = useCallback((value: string, placeDetails?: google.maps.places.PlaceResult) => {
    console.debug('🗺️ CreateAccountModal: Place selected:', { value, placeDetails });
    
    // Update Address Line 1 with the selected address
    handleAddressChange('line1', value);
    
    if (placeDetails?.address_components) {
      const components = placeDetails.address_components;
      
      // Extract address components
      const streetNumber = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('street_number'))?.long_name || '';
      const route = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('route'))?.long_name || '';
      const sublocality = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('sublocality'))?.long_name;
      const locality = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('locality'))?.long_name;
      const pincode = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('postal_code'))?.long_name;
      const city = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('administrative_area_level_3'))?.long_name;
      const stateComponent = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('administrative_area_level_1'))?.long_name;

      // Set line1 (street address)
      const line1Components = [streetNumber, route].filter(Boolean);
      const line1 = line1Components.join(' ');
      if (line1) {
        handleAddressChange('line1', line1);
      }
      
      // Get additional address components for line2
      const premise = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('premise'))?.long_name;
      const subpremise = components.find((c: google.maps.GeocoderAddressComponent) => 
        c.types.includes('subpremise'))?.long_name;
      
      // Set line2 (combine subpremise, premise, and sublocality)
      const line2Components = [subpremise, premise, sublocality].filter(Boolean);
      if (line2Components.length > 0) {
        handleAddressChange('line2', line2Components.join(', '));
      }
      
      // Set city (prefer administrative_area_level_3, fallback to locality)
      const cityValue = city || locality;
      if (cityValue) {
        handleAddressChange('city', cityValue);
      }
      
      // Set state (map Google Maps state to US_STATES array)
      if (stateComponent) {
        const matchedState = US_STATES.find(state => 
          state.toLowerCase() === stateComponent.toLowerCase()
        );
        if (matchedState) {
          handleAddressChange('state', matchedState);
        }
      }
      
      // Set pincode if available
      if (pincode) {
        const numericPincode = parseInt(pincode, 10);
        if (!isNaN(numericPincode)) {
          handleAddressChange('pincode', numericPincode);
        }
      }

      console.debug('🗺️ CreateAccountModal: Address components extracted:', {
        line1,
        line2: line2Components.join(', '),
        city: cityValue,
        state: stateComponent,
        pincode: pincode ? parseInt(pincode, 10) : null
      });
    }
  }, [handleAddressChange]);

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
      // Strip the state field from client_address before sending to backend
      const { state, ...addressWithoutState } = formData.client_address;
      const backendFormData: AccountCreate = {
        ...formData,
        client_address: addressWithoutState,
      };
      
      console.debug('🚀 CreateAccountModal: Submitting form data:', backendFormData);
      await onSubmit(backendFormData);
      // resetForm();
    } catch (error) {
      console.error('Form submission error:', error);
      // Handle submission error if needed
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, onSubmit]);

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
    handleAddressChange,
    handlePlaceSelect,
    handleSubmit,
    handleClose,
    resetForm,
  };
}
