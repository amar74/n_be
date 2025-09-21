import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Globe } from 'lucide-react';
import { UIAccountFormData } from '../../CreateAccountModal.types';

interface CompanyWebsiteFormProps {
  value: string | null | undefined;
  onChange: (value: string) => void;
  isAnalyzing?: boolean;
  showAISuggestions?: boolean;
  error?: string;
}

export function CompanyWebsiteForm({ value, onChange, isAnalyzing = false, showAISuggestions = false, error }: CompanyWebsiteFormProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-4 items-center">
        <div className="bg-[#eeeeee] p-2 rounded-full">
          <Sparkles className="h-6 w-6 text-orange-400" />
        </div>
        <div className="flex items-center gap-4">
          <Label className="text-lg sm:text-xl font-medium text-[#0f0901] capitalize">
            Company website
          </Label>
          <Badge
            variant="secondary"
            className="bg-[#ED8A09] text-white text-xs px-3 py-0 rounded-2xl flex items-center gap-1"
          >
            <Sparkles className="h-3 w-3 text-white" /> AI Enhanced
          </Badge>
        </div>
      </div>
      <div className="relative">
        <div className="absolute left-3 top-1/2 transform -translate-y-1/2">
          <Globe className="h-5 w-5 text-gray-400" />
        </div>
        <Input
          type="url"
          placeholder="https://your-company.com"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className={`pl-10 h-12 sm:h-14 bg-[#f3f3f3] border-[#e6e6e6] rounded-xl text-[#2277f6] focus:bg-white focus:border-[#ff7b00] focus:outline-none focus:ring-0 focus-visible:ring-0 ${
            showAISuggestions && value ? 'bg-green-50 border-green-200' : ''
          } ${error ? 'border-red-500' : ''}`}
        />
        {error && (
          <span className="text-red-500 text-sm mt-1">{error}</span>
        )}
      </div>
      {value &&
        value.includes('.') &&
        isAnalyzing &&
        !showAISuggestions && (
          <div className="flex items-center gap-2 text-sm text-purple-600">
            <Sparkles className="h-4 w-4" />
            <span>AI will analyze website and auto-populate fields...</span>
          </div>
        )}
    </div>
  );
}
