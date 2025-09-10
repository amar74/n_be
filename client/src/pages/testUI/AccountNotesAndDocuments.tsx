import React, { useState, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Select, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover";
import { Calendar as CalendarIcon, Files } from "phosphor-react";

export function AccountNotesAndDocuments() {
  const [date, setDate] = React.useState<Date | undefined>(new Date());
  const [datebutton, setDateButton] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const toggleDateButton = () => setDateButton((prev) => !prev);


  // format date as DD/MM/YYYY
  const formatDate = (d?: Date) => {
    if (!d) return "DD/MM/YYYY";
    const dd = String(d.getDate()).padStart(2, "0");
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    const yyyy = d.getFullYear();
    return `${dd}/${mm}/${yyyy}`;
  };

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    console.log("files selected:", files);
  };

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  return (
    <div className="flex flex-col gap-3 mt-2">
      {/* Account Notes */}
      <Card className="rounded-xl shadow-sm border border-gray-200 bg-white">
        <CardHeader className="py-2 px-4">
          <CardTitle className="text-base font-semibold">Account Notes</CardTitle>
        </CardHeader>

        <CardContent className="space-y-3 py-2 px-4">
          {/* Top Row */}
          <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
            <Input placeholder="Title for the note..." className="flex-1 h-9 text-sm bg-[#F3F3F3] border-[#E6E6E6]  focus:border-[#FF7B00] focus:outline-none focus:ring-0 focus-visible:ring-0" />

            {/* Category Select */}
            <Select>
              <SelectTrigger className="w-40 h-9 bg-[#ED8A09] text-white text-sm font-medium rounded-md">
                <SelectValue placeholder="Select Category" />
              </SelectTrigger>
            </Select>

            {/* Date Picker */}
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  onClick={toggleDateButton}
                  className={`flex items-center gap-2 w-[150px] h-9 text-sm justify-start rounded-md ${
                    datebutton ? "bg-black text-white" : "bg-white text-black"
                  }`}
                >
                  <CalendarIcon size={16} />
                  {formatDate(date)}
                </Button>
              </PopoverTrigger>
              <PopoverContent
                side="bottom"
                align="start"
                className="w-auto p-0 bg-white rounded-2xl"
              >
                <Calendar
                  mode="single"
                  selected={date}
                  onSelect={setDate}
                  captionLayout="dropdown"
                  className="rounded-2xl border shadow-sm"
                  classNames={{
                    day_selected:
                      "bg-[#ED8A09] text-white hover:bg-[#d97706] hover:text-white " +
                      "focus:bg-[#d97706] focus:text-white aria-selected:bg-[#ED8A09] aria-selected:text-white",
                    day_today: "bg-orange-100 text-[#ED8A09] font-semibold",
                    head_cell: "text-gray-600 font-medium",
                    cell: "text-center p-0 relative first:[&:has([aria-selected])]:rounded-l-md last:[&:has([aria-selected])]:rounded-r-md focus-within:relative focus-within:z-20",
                    day: "h-9 w-9 p-0 font-normal aria-selected:opacity-100 hover:bg-orange-100 hover:text-[#ED8A09]",
                    day_range_middle: "aria-selected:bg-[#ED8A09] aria-selected:text-white",
                    day_outside:
                      "text-gray-400 opacity-50 aria-selected:bg-[#ED8A09] aria-selected:text-white aria-selected:opacity-70",
                    caption_dropdowns: "flex justify-center gap-1",
                    dropdown_month: "text-[#ED8A09] font-medium",
                    dropdown_year: "text-[#ED8A09] font-medium",
                  }}
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Notes Textarea */}
          <Textarea
            placeholder="Add strategic notes, relationship insights, and important observations..."
            rows={2}
            className="py-2 text-sm bg-[#F3F3F3] border-[#E6E6E6]  focus:border-[#FF7B00] focus:outline-none focus:ring-0 focus-visible:ring-0 resize-none"
          />
        </CardContent>
      </Card>

      {/* Account Documents */}
      <Card className="rounded-xl shadow-sm border border-gray-200 bg-white">
        <CardHeader className="py-2 px-4">
          <div className="flex items-center justify-between border-b border-gray-200 pb-2">
            <div>
              <CardTitle className="text-base font-semibold">Account Documents</CardTitle>
              <p className="text-xs text-[#A7A7A7] font-normal">
                Upload presentations and documents for this account
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="py-3 px-4">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            hidden
            onChange={(e) => handleFiles(e.target.files)}
            accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,image/*"
          />

          <div
            onDrop={onDrop}
            onDragOver={onDragOver}
            onClick={() => fileInputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-4 flex flex-col items-center justify-center text-center space-y-2 cursor-pointer hover:border-gray-400"
            style={{ minHeight: 88 }}
          >
            <Files size={20} className="text-gray-500" />
            <div className="flex items-center gap-1 text-sm text-gray-700">
              <span>Drag and drop files here, or</span>
              <button
                type="button"
                className="text-[#ED8A09] font-medium underline"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                click to upload
              </button>
            </div>
            <p className="text-xs text-gray-500">PDF, DOC, PPT, XLS, and images support</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
