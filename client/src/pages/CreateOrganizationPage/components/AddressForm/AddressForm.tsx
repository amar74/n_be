import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { MapPin } from 'lucide-react';
import { PlacesAutocomplete } from '@/components/ui/places-autocomplete';
import type { AddressFormProps } from '../../CreateOrganizationPage.types';

export function AddressForm({ control, isSubmitting, showAISuggestions }: AddressFormProps) {
  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Address</h3>
      
      {/* Address Line 1 with Google Places */}
      <FormField
        control={control}
        name="address.line1"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm font-medium">
              Address Line 1 *
            </FormLabel>
            <FormControl>
              <PlacesAutocomplete
                value={field.value || ''}
                onChange={(value, placeDetails) => {
                  // Update line1 with the selected address
                  field.onChange(value);
                  
                  if (placeDetails?.address_components) {
                    // Extract address components
                    const components = placeDetails.address_components;
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
                    
                    // Set line1 (street address)
                    const line1 = [streetNumber, route].filter(Boolean).join(' ');
                    control.setValue('address.line1', line1, { shouldValidate: true });
                    
                    // Set line2 (sublocality)
                    if (sublocality) {
                      control.setValue('address.line2', sublocality, { shouldValidate: true });
                    }
                    
                    // Set city (locality)
                    if (locality) {
                      control.setValue('address.city', locality, { shouldValidate: true });
                    }
                    
                    // Set pincode if available
                    if (pincode) {
                      control.setValue('address.pincode', parseInt(pincode), { shouldValidate: true });
                    }
                  }
                }}
                placeholder="Search for an address"
                className={showAISuggestions && field.value ? 'bg-green-50 border-green-200' : ''}
                disabled={isSubmitting}
              />
            </FormControl>
            <div className="h-4 mt-0.5">
              <FormMessage className="text-red-500 text-xs" />
            </div>
          </FormItem>
        )}
      />

      {/* Address Line 2 */}
      <FormField
        control={control}
        name="address.line2"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm font-medium">
              Address Line 2
            </FormLabel>
            <FormControl>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  {...field}
                  value={field.value || ''}
                  placeholder="Apartment, suite, unit, etc."
                  className="pl-10 border 
                    placeholder-shown:border-gray-300 
                    focus:border-orange-300 
                    not-placeholder-shown:border-orange-300 
                    focus:outline-none focus:ring-0 focus-visible:ring-0"
                  disabled={isSubmitting}
                />
              </div>
            </FormControl>
            <div className="h-4 mt-0.5">
              <FormMessage className="text-red-500 text-xs" />
            </div>
          </FormItem>
        )}
      />

      {/* City */}
      <FormField
        control={control}
        name="address.city"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm font-medium">
              City
            </FormLabel>
            <FormControl>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  {...field}
                  value={field.value || ''}
                  placeholder="Enter city"
                  className={`pl-10 border 
                    placeholder-shown:border-gray-300 
                    focus:border-orange-300 
                    not-placeholder-shown:border-orange-300 
                    focus:outline-none focus:ring-0 focus-visible:ring-0 ${
                      showAISuggestions && field.value ? 'bg-green-50 border-green-200' : ''
                    }`}
                  disabled={isSubmitting}
                />
              </div>
            </FormControl>
            <div className="h-4 mt-0.5">
              <FormMessage className="text-red-500 text-xs" />
            </div>
          </FormItem>
        )}
      />

      {/* Postal Code */}
      <FormField
        control={control}
        name="address.pincode"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm font-medium">
              Postal Code
            </FormLabel>
            <FormControl>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  {...field}
                  value={field.value || ''}
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  placeholder="Enter postal code (5-6 digits)"
                  className="pl-10 border 
                    placeholder-shown:border-gray-300 
                    focus:border-orange-300 
                    not-placeholder-shown:border-orange-300 
                    focus:outline-none focus:ring-0 focus-visible:ring-0"
                  disabled={isSubmitting}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, ''); // Remove non-digits
                    const numValue = value ? parseInt(value) : undefined;
                    field.onChange(numValue);
                  }}
                  maxLength={6}
                />
              </div>
            </FormControl>
            <div className="h-4 mt-0.5">
              <FormMessage className="text-red-500 text-xs" />
            </div>
          </FormItem>
        )}
      />
    </div>
  );
}
