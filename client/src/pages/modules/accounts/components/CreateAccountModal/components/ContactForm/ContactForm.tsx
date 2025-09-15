import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CreateAccountFormData } from '../../CreateAccountModal.types';

interface ContactFormProps {
  formData: CreateAccountFormData;
  errors: Record<string, string>;
  onChange: (field: keyof CreateAccountFormData, value: string) => void;
}

export function ContactForm({ formData, errors, onChange }: ContactFormProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 sm:gap-7">
      <div className="flex-1 flex flex-col gap-3">
        <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
          Primary Contact
        </Label>
        <Input
          placeholder="Contact Name"
          value={formData.primaryContact}
          onChange={(e) => onChange('primaryContact', e.target.value)}
          className="h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0"
        />
      </div>
      <div className="flex-1 flex flex-col gap-3">
        <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
          Contact Email
        </Label>
        <Input
          type="email"
          placeholder="Email address"
          value={formData.contactEmail}
          onChange={(e) => onChange('contactEmail', e.target.value)}
          className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
            errors.contactEmail ? 'border-red-500' : ''
          }`}
        />
        {errors.contactEmail && (
          <span className="text-red-500 text-sm">{errors.contactEmail}</span>
        )}
      </div>
    </div>
  );
}
