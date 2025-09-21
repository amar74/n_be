import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PlacesAutocomplete } from '@/components/ui/places-autocomplete';
import { UIAccountFormData, UIAddressData } from '../../CreateAccountModal.types';
import { US_STATES } from '../../CreateAccountModal.constants';

interface AddressFormProps {
  formData: UIAccountFormData;
  errors: Record<string, string>;
  onChange: (field: string, value: string | object) => void;
  onAddressChange: (field: keyof UIAddressData, value: string | number | null) => void;
  onPlaceSelect: (value: string, placeDetails?: google.maps.places.PlaceResult) => void;
  showAISuggestions?: boolean;
}

export function AddressForm({ formData, errors, onChange, onAddressChange, onPlaceSelect, showAISuggestions = false }: AddressFormProps) {
  const handleAddressChange = (field: keyof UIAddressData, value: string) => {
    const processedValue = field === 'pincode' ? (value ? parseInt(value, 10) : null) : value;
    onAddressChange(field, processedValue);
  };

  return (
    <>
      {/* Client Name */}
      <div className="flex flex-col gap-3">
        <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
          Client Name *
        </Label>
          <Input
            placeholder="Company Name"
            value={formData.client_name || ''}
            onChange={(e) => onChange('client_name', e.target.value)}
          className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
            errors.client_name ? 'border-red-500' : ''
          } ${showAISuggestions && formData.client_name ? 'bg-green-50 border-green-200' : ''}`}
        />
        {errors.client_name && (
          <span className="text-red-500 text-sm">{errors.client_name}</span>
        )}
      </div>

      {/* Address Fields */}
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-7">
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Client Address 1 *
          </Label>
          <PlacesAutocomplete
            value={formData.client_address.line1}
            onChange={onPlaceSelect}
            placeholder="Search for an address"
            className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors['client_address.line1'] ? 'border-red-500' : ''
            } ${showAISuggestions && formData.client_address.line1 ? 'bg-green-50 border-green-200' : ''}`}
            disabled={false}
          />
          {errors['client_address.line1'] && (
            <span className="text-red-500 text-sm">{errors['client_address.line1']}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Client Address 2
          </Label>
          <Input
            placeholder="Billing address (auto-fill by AI)"
            value={formData.client_address.line2 || ''}
            onChange={(e) => handleAddressChange('line2', e.target.value)}
            className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              showAISuggestions && formData.client_address.line2 ? 'bg-green-50 border-green-200' : ''
            }`}
          />
        </div>
      </div>

      {/* City, State, Zip */}
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-7">
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            City *
          </Label>
          <Input
            placeholder="City Name"
            value={formData.client_address.city || ''}
            onChange={(e) => handleAddressChange('city', e.target.value)}
            className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors['client_address.city'] ? 'border-red-500' : ''
            } ${showAISuggestions && formData.client_address.city ? 'bg-green-50 border-green-200' : ''}`}
          />
          {errors['client_address.city'] && (
            <span className="text-red-500 text-sm">{errors['client_address.city']}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            State *
          </Label>
          <Select 
            value={formData.client_address.state || ''}
            onValueChange={(value) => handleAddressChange('state', value)}
          >
            <SelectTrigger className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors['client_address.state'] ? 'border-red-500' : ''
            } ${showAISuggestions && formData.client_address.state ? 'bg-green-50 border-green-200' : ''}`}>
              <SelectValue placeholder="Select State" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {US_STATES.map((state) => (
                <SelectItem key={state} value={state}>
                  {state}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors['client_address.state'] && (
            <span className="text-red-500 text-sm">{errors['client_address.state']}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Zip Code
          </Label>
          <Input
            placeholder="Zip Code"
            value={formData.client_address.pincode?.toString() || ''}
            onChange={(e) => handleAddressChange('pincode', e.target.value)}
            className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors['client_address.pincode'] ? 'border-red-500' : ''
            } ${showAISuggestions && formData.client_address.pincode ? 'bg-green-50 border-green-200' : ''}`}
          />
          {errors['client_address.pincode'] && (
            <span className="text-red-500 text-sm">{errors['client_address.pincode']}</span>
          )}
        </div>
      </div>
    </>
  );
}
