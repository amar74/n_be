import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CreateAccountFormData } from '../../CreateAccountModal.types';
import { MARKET_SECTORS, CLIENT_TYPES, HOSTING_AREAS, MSA_OPTIONS } from '../../CreateAccountModal.constants';

interface BusinessFormProps {
  formData: CreateAccountFormData;
  errors: Record<string, string>;
  onChange: (field: keyof CreateAccountFormData, value: string) => void;
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
          <Select value={formData.clientMarketSector} onValueChange={(value) => onChange('clientMarketSector', value)}>
            <SelectTrigger className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors.clientMarketSector ? 'border-red-500' : ''
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
          {errors.clientMarketSector && (
            <span className="text-red-500 text-sm">{errors.clientMarketSector}</span>
          )}
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Client type *
          </Label>
          <Select value={formData.clientType} onValueChange={(value) => onChange('clientType', value)}>
            <SelectTrigger className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
              errors.clientType ? 'border-red-500' : ''
            }`}>
              <SelectValue placeholder="Select tire" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {CLIENT_TYPES.map((type) => (
                <SelectItem key={type} value={type}>
                  {type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.clientType && (
            <span className="text-red-500 text-sm">{errors.clientType}</span>
          )}
        </div>
      </div>

      {/* Hosting Area and MSA */}
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-7">
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            Hosting Area/Office
          </Label>
          <Select value={formData.hostingArea} onValueChange={(value) => onChange('hostingArea', value)}>
            <SelectTrigger className="h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0">
              <SelectValue placeholder="Select office" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {HOSTING_AREAS.map((area) => (
                <SelectItem key={area} value={area}>
                  {area}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex-1 flex flex-col gap-3">
          <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
            MSA in place
          </Label>
          <Select value={formData.msaInPlace} onValueChange={(value) => onChange('msaInPlace', value)}>
            <SelectTrigger className="h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0">
              <SelectValue placeholder="Select" />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {MSA_OPTIONS.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </>
  );
}
