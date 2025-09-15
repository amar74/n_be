import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Sparkles, Globe } from 'lucide-react';
import { CreateAccountFormData } from '../../CreateAccountModal.types';

interface CompanyWebsiteFormProps {
  value: string | undefined;
  onChange: (field: keyof CreateAccountFormData, value: string) => void;
}

export function CompanyWebsiteForm({ value, onChange }: CompanyWebsiteFormProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-4 items-center">
        <div className="bg-[#eeeeee] p-2 rounded-full">
          <Sparkles className="h-6 w-6 text-orange-400" />
        </div>
        <Label className="text-lg sm:text-xl font-medium text-[#0f0901] capitalize">
          Company website (AI smart population)
        </Label>
      </div>
      <div className="relative">
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
          <Globe className="h-5 w-5 text-gray-400" />
        </div>
        <Input
          type="url"
          placeholder="https://your-company.com"
          value={value || ''}
          onChange={(e) => onChange('companyWebsite', e.target.value)}
          className="pl-10 h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl text-[#2277f6] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0"
        />
      </div>
    </div>
  );
}
