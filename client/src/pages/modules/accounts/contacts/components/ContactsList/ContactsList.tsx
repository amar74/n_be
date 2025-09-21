import React from 'react';
import { Edit, Trash2, User, Crown } from 'lucide-react';

import { ContactResponse } from '@/types/accounts';
import { useAccountDetail } from '@/hooks/useAccounts';

interface ContactsListProps {
  contacts: ContactResponse[];
  onEdit: (contact: ContactResponse) => void;
  onDelete: (contactId: string) => void;
  isLoading?: boolean;
  accountId: string;
}

export function ContactsList({ accountId, contacts, onEdit, onDelete, isLoading = false }: ContactsListProps) {
  const formatPhone = (phone: string) => {
    // Simple phone formatting - you can enhance this
    return phone.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
  };
  const {accountDetail} = useAccountDetail(accountId)

  if (isLoading) {
    return (
      <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ed8a09]"></div>
        </div>
      </div>
    );
  }

  if (contacts.length === 0) {
    return (
      <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <User className="h-12 w-12 text-[#a7a7a7] mb-4" />
          <h3 className="font-inter font-semibold text-[#0f0901] text-[18px] mb-2">No Contacts Yet</h3>
          <p className="font-inter font-medium text-[#a7a7a7] text-[16px]">
            Add your first contact for this account using the form above.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
      <div className="flex flex-col gap-6 w-full">
        {/* Header */}
        <div className="flex flex-col gap-2">
          <h3 className="font-inter font-bold text-[#0f0901] text-[24px] leading-normal flex items-center gap-2">
            <User className="h-6 w-6" />
            Client Contact
          </h3>
          <p className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
            Manage client contact information
          </p>
        </div>

        {/* Divider */}
        <div className="h-px w-full bg-[#e6e6e6]" />

        {/* Contacts List */}
        <div className="flex flex-col gap-4 w-full">
          {contacts.map((contact) => {

            const isPrimaryContact = contact.contact_id === accountDetail?.primary_contact?.contact_id
            return (
            <div
              key={contact.contact_id}
              className="bg-white border border-[#dddddd] rounded-[20px] p-6 hover:border-[#d0d0d0] transition-colors"
            >
              <div className="flex items-center justify-between w-full">
                {/* Contact Information */}
                <div className="flex gap-4 flex-1 flex-wrap">
                  {/* Title */}
                  <div className="w-[160px] flex flex-col gap-3">
                    <div className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal capitalize">
                      Title
                    </div>
                    <div className="bg-[#f3f3f3] border border-[#e6e6e6] rounded-[14px] h-14 px-6 py-2 flex items-center">
                      <span className="font-inter font-semibold text-[#0f0901] text-[16px]">
                        {contact.title || ''}
                      </span>
                    </div>
                  </div>
                  {/* Name */}
                  <div className="flex-1 flex flex-col gap-3">
                    <div className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal capitalize">
                      Name
                    </div>
                    <div className="bg-[#f3f3f3] border border-[#e6e6e6] rounded-[14px] h-14 px-6 py-2 flex items-center">
                      <span className="font-inter font-semibold text-[#0f0901] text-[16px]">
                        {contact.name}
                      </span>
                    </div>
                  </div>
                  {/* Email */}
                  <div className="flex-1 flex flex-col gap-3">
                    <div className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal capitalize">
                      E-Mail
                    </div>
                    <div className="bg-[#f3f3f3] border border-[#e6e6e6] rounded-[14px] h-14 px-6 py-2 flex items-center">
                      <span className="font-inter font-semibold text-[#0f0901] text-[16px] overflow-hidden text-ellipsis whitespace-nowrap">
                        {contact.email}
                      </span>
                    </div>
                  </div>
                  {/* Phone */}
                  <div className="flex-1 flex flex-col gap-3">
                    <div className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal capitalize">
                      Phone
                    </div>
                    <div className="bg-[#f3f3f3] border border-[#e6e6e6] rounded-[14px] h-14 px-6 py-2 flex items-center">
                      <span className="font-inter font-semibold text-[#0f0901] text-[16px]">
                        {formatPhone(contact.phone)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Status and Actions */}
                <div className="flex flex-col gap-3 items-end ml-6">
                  <div className="font-inter font-medium text-[16px] leading-normal capitalize">
                    Status
                  </div>
                  <div className="flex items-center gap-3">
                    {/* Status Badge */}
                    <div className={`
                      px-3 py-2 rounded-[12px] flex items-center gap-2 min-w-[100px] justify-center
                      ${isPrimaryContact 
                        ? 'bg-[#ed8a09] text-[#dfdfdf]' 
                        : 'bg-[#f3f3f3] text-[#0f0901] border border-[#e6e6e6]'
                      }
                    `}>
                      <span className="font-inter font-semibold text-[14px] capitalize">
                        {isPrimaryContact ? 'Primary' : 'Secondary'}
                      </span>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => onEdit(contact)}
                        className="bg-[#f3f3f3] hover:bg-[#e8e8e8] border border-[#e6e6e6] rounded-[8px] p-2 transition-colors"
                        title="Edit Contact"
                      >
                        <Edit className="h-4 w-4 text-[#0f0901]" />
                      </button>
                      {!isPrimaryContact && (
                        <button
                          onClick={() => onDelete(contact.contact_id)}
                          className="bg-[#fee2e2] hover:bg-[#fecaca] border border-[#fca5a5] rounded-[8px] p-2 transition-colors"
                          title="Delete Contact"
                        >
                          <Trash2 className="h-4 w-4 text-[#dc2626]" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )})}
        </div>
      </div>
    </div>
  );
}
