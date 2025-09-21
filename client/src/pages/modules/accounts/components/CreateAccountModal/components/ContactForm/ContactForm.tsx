import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { UIAccountFormData } from '../../CreateAccountModal.types';

interface ContactFormProps {
  formData: UIAccountFormData;
  errors: Record<string, string>;
  onChange: (field: string, value: string | object) => void;
}

export function ContactForm({ formData, errors, onChange }: ContactFormProps) {
  const handleContactChange = (field: keyof UIAccountFormData['primary_contact'], value: string) => {
    onChange('primary_contact', {
      ...formData.primary_contact,
      [field]: value,
    });
  };

  return (
    <div className="flex flex-col sm:flex-row gap-4 sm:gap-7">
      <div className="flex-1 flex flex-col gap-3">
        <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
          Primary Contact Name *
        </Label>
        <Input
          placeholder="Contact Name"
          value={formData.primary_contact.name}
          onChange={(e) => handleContactChange('name', e.target.value)}
          className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
            errors['primary_contact.name'] ? 'border-red-500' : ''
          }`}
        />
        {errors['primary_contact.name'] && (
          <span className="text-red-500 text-sm">{errors['primary_contact.name']}</span>
        )}
      </div>
      <div className="flex-1 flex flex-col gap-3">
        <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
          Contact Email *
        </Label>
        <Input
          type="email"
          placeholder="Email address"
          value={formData.primary_contact.email}
          onChange={(e) => handleContactChange('email', e.target.value)}
          className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
            errors['primary_contact.email'] ? 'border-red-500' : ''
          }`}
        />
        {errors['primary_contact.email'] && (
          <span className="text-red-500 text-sm">{errors['primary_contact.email']}</span>
        )}
      </div>
      <div className="flex-1 flex flex-col gap-3">
        <Label className="text-base sm:text-lg font-medium text-[#0f0901] capitalize">
          Contact Phone *
        </Label>
        <Input
          type="tel"
          placeholder="Phone number"
          value={formData.primary_contact.phone}
          onChange={(e) => handleContactChange('phone', e.target.value)}
          className={`h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl px-4 sm:px-6 text-sm sm:text-base font-medium placeholder:text-[#a7a7a7] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
            errors['primary_contact.phone'] ? 'border-red-500' : ''
          }`}
        />
        {errors['primary_contact.phone'] && (
          <span className="text-red-500 text-sm">{errors['primary_contact.phone']}</span>
        )}
      </div>
    </div>
  );
}
