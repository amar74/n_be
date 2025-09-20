import React from 'react';
import { ChevronDown } from 'lucide-react';
import { AccountFormData } from '../../../AccountDetailsPage.types';
import { CLIENT_TYPES, FORM_FIELD_LABELS } from '../../../AccountDetailsPage.constants';
import { US_STATES } from '../../../components/CreateAccountModal/CreateAccountModal.constants';

interface AccountInformationFormProps {
  formData: AccountFormData;
  accountId?: string;
  isEditing: boolean;
  isUpdating: boolean;
  onFormChange: (field: keyof AccountFormData, value: any) => void;
  onSave: () => void;
  onCancel: () => void;
}

export function AccountInformationForm({
  formData,
  accountId,
  isEditing,
  isUpdating,
  onFormChange,
  onSave,
  onCancel,
}: AccountInformationFormProps) {
  const renderField = (
    field: keyof AccountFormData,
    type: 'text' | 'select' | 'boolean' = 'text',
    options?: Array<{ value: string; label: string }>,
    width: 'full' | 'narrow' = 'full'
  ) => {
    const value = formData[field];
    const label = FORM_FIELD_LABELS[field];
    const isActive = isEditing && value !== '';
    
    const baseClasses = `
      flex flex-col gap-3 items-start justify-start relative self-stretch shrink-0
      ${width === 'narrow' ? 'w-[187px]' : 'flex-1 min-w-0'}
    `;
    
    const inputClasses = `
      ${isActive ? 'bg-white border-[#ff7b00]' : 'bg-[#f3f3f3] border-[#e6e6e6]'}
      border border-solid rounded-[14px] h-14 flex items-center justify-between px-6 py-2 w-full
      ${isActive ? 'ring-1 ring-[#ff7b00]' : ''}
    `;

    return (
      <div className={baseClasses}>
        <label className="font-inter font-medium text-[#a7a7a7] text-[16px] capitalize leading-normal w-full">
          {label}
        </label>
        
        {type === 'select' ? (
          <div className="relative w-full">
            <select
              value={value as string}
              onChange={(e) => onFormChange(field, e.target.value)}
              disabled={!isEditing}
              className={`${inputClasses} appearance-none cursor-pointer font-inter font-semibold text-[#0f0901] text-[16px]`}
            >
              {options?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-6 top-1/2 transform -translate-y-1/2 h-5 w-5 text-[#6c6c6c] pointer-events-none" />
          </div>
        ) : type === 'boolean' ? (
          <div className={`${inputClasses} ${formData.msa_in_place ? 'bg-[rgba(237,138,9,0.2)]' : ''}`}>
            <span className={`font-inter font-semibold text-[16px] ${formData.msa_in_place ? 'text-[#ff8500]' : 'text-[#0f0901]'}`}>
              {formData.msa_in_place ? 'Yes' : 'No'}
            </span>
          </div>
        ) : (
          <input
            type={type}
            value={value as string}
            onChange={(e) => onFormChange(field, e.target.value)}
            disabled={!isEditing}
            className={`${inputClasses} font-inter font-semibold text-[#0f0901] text-[16px] leading-normal`}
            placeholder={isEditing ? `Enter ${label.toLowerCase()}` : ''}
          />
        )}
      </div>
    );
  };

  return (
    <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-[1019px]">
      <div className="flex flex-col gap-5 w-full">
        {/* Header */}
        <div className="flex flex-col gap-4 w-full">
          <div className="flex flex-col gap-7 w-full">
            <div className="flex flex-col gap-2">
              <h2 className="font-inter font-bold text-[#0f0901] text-[24px] leading-normal">
                Account information
              </h2>
            </div>
          </div>
          <p className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
            Complete account overview and profile details
          </p>
        </div>

        {/* Divider */}
        <div className="h-px w-full bg-[#e6e6e6]" />

        {/* Form Fields */}
        <div className="flex flex-col gap-6 w-full">
          {/* Row 1: Account ID + Client Name */}
          <div className="flex gap-3 w-full">
            {/* Account ID - Read Only */}
            <div className="flex flex-col gap-3 items-start justify-start relative self-stretch shrink-0 w-[300px]">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] capitalize leading-normal w-full">
                Account ID
              </label>
              <div className="bg-[#f3f3f3] border border-[#e6e6e6] border-solid rounded-[14px] h-14 flex items-center justify-between px-6 py-2 w-full">
                <span className="font-inter font-medium text-[#0f0901] text-[12px] leading-normal overflow-hidden text-ellipsis whitespace-nowrap">
                  {accountId || 'N/A'}
                </span>
              </div>
            </div>
            {renderField('client_name', 'text')}
          </div>

          {/* Row 2: Client Type + Market Sector */}
          <div className="flex gap-3 w-full">
            {renderField('client_type', 'select', CLIENT_TYPES)}
            {renderField('market_sector', 'text')}
          </div>

          {/* Row 3: Address */}
          <div className="flex flex-col gap-3 h-[87px] w-full">
            {renderField('client_address_line1', 'text')}
            {renderField('client_address_line2', 'text')}
          </div>

          {/* Row 4: City + State + Zip Code */}
          <div className="flex gap-7 w-full">
            {renderField('client_address_city', 'text')}
            {renderField('client_address_state', 'select', US_STATES.map((state) => ({ value: state, label: state })))}
            {renderField('client_address_zip_code', 'text')}
          </div>

          {/* Row 5: Website + Hosting Area + MSA */}
          <div className="flex gap-3 w-full">
            {renderField('company_website', 'text')}
            {renderField('hosting_area', 'text', undefined, 'narrow')}
            {renderField('msa_in_place', 'boolean', undefined, 'narrow')}
          </div>

          {/* Row 6: Account Approver + Approval Date */}
          <div className="flex gap-3 w-full">
            {renderField('account_approver', 'text')}
            {renderField('approval_date_time', 'text')}
          </div>
        </div>

        {/* Action Buttons */}
        {isEditing && (
          <div className="flex items-center justify-between w-full pt-4">
            <button
              onClick={onCancel}
              disabled={isUpdating}
              className="bg-transparent border border-[#0f0901] rounded-[16px] h-14 flex items-center justify-center px-6 py-2 min-w-[148px]"
            >
              <span className="font-inter font-medium text-[#0f0901] text-[14px] leading-[24px]">
                Cancel
              </span>
            </button>
            <button
              onClick={onSave}
              disabled={isUpdating}
              className="bg-[#0f0901] rounded-[16px] h-14 flex items-center justify-center px-8 py-2 min-w-[200px] ml-4"
            >
              <span className="font-inter font-medium text-white text-[14px] leading-[24px]">
                {isUpdating ? 'Saving...' : 'Save Changes'}
              </span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
