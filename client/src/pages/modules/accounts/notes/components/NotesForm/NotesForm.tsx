import React, { useState, useEffect } from 'react';
import { ChevronDown, Calendar, FileText } from 'lucide-react';
import { NoteFormData, NoteCategory } from '../../NotesTab.types';
import { NOTE_CATEGORIES } from '../../NotesTab.constants';

interface NotesFormProps {
  onSubmit: (note: NoteFormData) => Promise<any>;
  isLoading?: boolean;
  initialData?: Partial<NoteFormData>;
  onCancel?: () => void;
  defaultFormValues: NoteFormData;
}

export function NotesForm({ 
  onSubmit, 
  isLoading = false, 
  initialData = {}, 
  onCancel,
  defaultFormValues 
}: NotesFormProps) {
  const [formData, setFormData] = useState<NoteFormData>({
    ...defaultFormValues,
    ...initialData,
  });

  useEffect(() => {
    setFormData({
      ...defaultFormValues,
      ...initialData,
    });
  }, [initialData, defaultFormValues]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.content.trim()) {
      return;
    }

    try {
      await onSubmit(formData);
      
      // Reset form if it's a create operation (no initial data)
      if (!initialData.title) {
        setFormData(defaultFormValues);
      }
    } catch (error) {
      // Error handling is done in the hook
    }
  };

  const handleChange = (field: keyof NoteFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <div className="bg-neutral-50 border border-[#f0f0f0] rounded-[28px] p-6 w-full">
      <div className="flex flex-col gap-6 w-full">
        {/* Header */}
        <div className="flex flex-col gap-2">
          <h2 className="font-inter font-bold text-[#0f0901] text-[24px] leading-normal flex items-center gap-2">
            <FileText className="h-6 w-6" />
            {initialData.title ? 'Edit Note' : 'Add New Note'}
          </h2>
          <p className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
            {initialData.title ? 'Update your note details' : 'Create a new note for this account'}
          </p>
        </div>

        {/* Divider */}
        <div className="h-px w-full bg-[#e6e6e6]" />

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-6 w-full">
          {/* Row 1: Title + Category + Date */}
          <div className="flex gap-4 w-full">
            {/* Title */}
            <div className="flex-1 flex flex-col gap-3">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
                Note Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                placeholder="Enter note title"
                required
                className="bg-white border border-[#e6e6e6] rounded-[14px] h-14 px-6 py-2 font-inter font-medium text-[#0f0901] text-[16px] focus:border-[#ff7b00] focus:outline-none"
              />
            </div>

            {/* Category */}
            <div className="w-[280px] flex flex-col gap-3">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
                Category *
              </label>
              <div className="relative">
                <select
                  value={formData.category}
                  onChange={(e) => handleChange('category', e.target.value)}
                  required
                  className="bg-white border border-[#e6e6e6] rounded-[14px] h-14 px-6 py-2 font-inter font-medium text-[#0f0901] text-[16px] w-full appearance-none cursor-pointer focus:border-[#ff7b00] focus:outline-none"
                >
                  {NOTE_CATEGORIES.map((category) => (
                    <option key={category.value} value={category.value}>
                      {category.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-6 top-1/2 transform -translate-y-1/2 h-5 w-5 text-[#6c6c6c] pointer-events-none" />
              </div>
            </div>

            {/* Date */}
            <div className="w-[200px] flex flex-col gap-3">
              <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Date *
              </label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => handleChange('date', e.target.value)}
                required
                className="bg-white border border-[#e6e6e6] rounded-[14px] h-14 px-6 py-2 font-inter font-medium text-[#0f0901] text-[16px] focus:border-[#ff7b00] focus:outline-none"
              />
            </div>
          </div>

          {/* Row 2: Content */}
          <div className="flex flex-col gap-3 w-full">
            <label className="font-inter font-medium text-[#a7a7a7] text-[16px] leading-normal">
              Note Content *
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => handleChange('content', e.target.value)}
              placeholder="Enter your note content here..."
              required
              rows={6}
              className="bg-white border border-[#e6e6e6] rounded-[14px] p-6 font-inter font-medium text-[#0f0901] text-[16px] resize-none focus:border-[#ff7b00] focus:outline-none"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-4 pt-4">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={isLoading}
                className="bg-transparent border border-[#0f0901] rounded-[16px] h-14 flex items-center justify-center px-6 py-2 min-w-[120px]"
              >
                <span className="font-inter font-medium text-[#0f0901] text-[14px] leading-[24px]">
                  Cancel
                </span>
              </button>
            )}
            <button
              type="submit"
              disabled={isLoading || !formData.title.trim() || !formData.content.trim()}
              className="bg-[#0f0901] rounded-[16px] h-14 flex items-center justify-center px-8 py-2 min-w-[160px] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="font-inter font-medium text-white text-[14px] leading-[24px]">
                {isLoading ? 'Saving...' : initialData.title ? 'Update Note' : 'Save Note'}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
