import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CreateAccountFormData } from '../../CreateAccountModal.types';
import { US_STATES } from '../../CreateAccountModal.constants';

interface AddressFormProps {
  formData: CreateAccountFormData;
  errors: Record<string, string>;
  onChange: (field: keyof CreateAccountFormData, value: string) => void;
}

export function AddressForm({ formData, errors, onChange }: AddressFormProps) {
  return (
    <>
      {/* Client Name */}
      <div className="flex flex-col gap-3">
        <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
          Client Name *
        </Label>
        <Input
          placeholder="Company Name"
          value={formData.clientName}
          onChange={(e) => onChange('clientName', e.target.value)}
          className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
            errors.clientName ? 'border-red-500' : ''
          }`}
        />
        {errors.clientName && (
          <span className="text-red-500 text-sm">{errors.clientName}</span>
        )}
      </div>

      {/* Address Fields */}
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-7">
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Client Address 1 *
          </Label>
          <Input
            placeholder="Billing address (auto-fill by AI)"
            value={formData.clientAddress1}
            onChange={(e) => onChange('clientAddress1', e.target.value)}
            className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors.clientAddress1 ? 'border-red-500' : ''
            }`}
          />
          {errors.clientAddress1 && (
            <span className="text-red-500 text-sm">{errors.clientAddress1}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Client Address 2
          </Label>
          <Input
            placeholder="Billing address (auto-fill by AI)"
            value={formData.clientAddress2}
            onChange={(e) => onChange('clientAddress2', e.target.value)}
            className="h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0"
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
            value={formData.city}
            onChange={(e) => onChange('city', e.target.value)}
            className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors.city ? 'border-red-500' : ''
            }`}
          />
          {errors.city && (
            <span className="text-red-500 text-sm">{errors.city}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            State *
          </Label>
          <Select value={formData.state} onValueChange={(value) => onChange('state', value)}>
            <SelectTrigger className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors.state ? 'border-red-500' : ''
            }`}>
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
          {errors.state && (
            <span className="text-red-500 text-sm">{errors.state}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Zip Code
          </Label>
          <Input
            placeholder="Zip Code"
            value={formData.zipCode}
            onChange={(e) => onChange('zipCode', e.target.value)}
            className="h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0"
          />
        </div>
      </div>
    </>
  );
}
