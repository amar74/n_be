import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ClientType } from '@/types/accounts';
import { UIAccountFormData } from '../../CreateAccountModal.types';
import { MARKET_SECTORS, CLIENT_TYPES, CLIENT_TYPE_DISPLAY } from '../../CreateAccountModal.constants';

interface BusinessFormProps {
  formData: UIAccountFormData;
  errors: Record<string, string>;
  onChange: (field: string, value: string) => void;
}

export function BusinessForm({ formData, errors, onChange }: BusinessFormProps) {
  return (
    <>
      {/* Market Sector and Client Type */}
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-7">
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Client Market Sector *
          </Label>
          <Select value={formData.market_sector || ''} onValueChange={(value) => onChange('market_sector', value)}>
            <SelectTrigger className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors.market_sector ? 'border-red-500' : ''
            }`}>
              <SelectValue placeholder="Select" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {MARKET_SECTORS.map((sector) => (
                <SelectItem key={sector} value={sector}>
                  {sector}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.market_sector && (
            <span className="text-red-500 text-sm">{errors.market_sector}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Client type *
          </Label>
          <Select value={formData.client_type} onValueChange={(value) => onChange('client_type', value)}>
            <SelectTrigger className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors.client_type ? 'border-red-500' : ''
            }`}>
              <SelectValue placeholder="Select tier" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {CLIENT_TYPES.map((type) => (
                <SelectItem key={type} value={type}>
                  {CLIENT_TYPE_DISPLAY[type]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.client_type && (
            <span className="text-red-500 text-sm">{errors.client_type}</span>
          )}
        </div>
      </div>
    </>
  );
}
