import React, { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Upload,
  FileText,
  Link as LinkIcon,
  Type,
  CheckCircle,
  AlertCircle,
  X,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  category: string;
  status: "uploading" | "completed" | "error";
}

export default function UploadTab() {
  const { toast } = useToast();
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [websiteLink, setWebsiteLink] = useState("");
  const [pastedText, setPastedText] = useState("");
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);

  // Document categories and their required items
  const documentCategories = {
    client: {
      title: "CLIENT DOCUMENTS",
      items: [
        {
          name: "RFP (client/project specific) with contract terms",
          obtained: true,
          source: "AI Web Research",
        },
        { name: "Addendums to RFP", obtained: false, source: "" },
        {
          name: "Past RFP(s) for similar services",
          obtained: true,
          source: "AI Web Research",
        },
        {
          name: "Available public data (EIR/EIS/presentations)",
          obtained: true,
          source: "AI Web Research",
        },
        {
          name: "Project Location (Google Maps)",
          obtained: true,
          source: "AI Web Research",
        },
        {
          name: "Client discussion notes and strategy",
          obtained: false,
          source: "",
        },
        { name: "Client Logo", obtained: true, source: "AI Web Research" },
        { name: "Project site pictures", obtained: false, source: "" },
        { name: "Team pictures at the site", obtained: false, source: "" },
        { name: "Award pictures with client", obtained: false, source: "" },
      ],
    },
    firm: {
      title: "FIRM DOCUMENTS",
      items: [
        { name: "Company Logo", obtained: true, source: "Pre-uploaded" },
        { name: "Past Proposals (Firm)", obtained: true, source: "Database" },
        {
          name: "Project data for qualifications section",
          obtained: true,
          source: "Database",
        },
        { name: "Past Awards", obtained: true, source: "Database" },
        { name: "References and quotes", obtained: false, source: "" },
        {
          name: "Graphics and design examples",
          obtained: true,
          source: "Database",
        },
        {
          name: "Text templates for sections",
          obtained: true,
          source: "Database",
        },
        {
          name: "Proposal design styles and themes",
          obtained: true,
          source: "Database",
        },
        {
          name: "Success stories and lessons learned",
          obtained: false,
          source: "",
        },
        { name: "Team/individual pictures", obtained: false, source: "" },
        { name: "Completed project photos", obtained: false, source: "" },
        { name: "Technical documentation", obtained: false, source: "" },
      ],
    },
    competition: {
      title: "COMPETITION ANALYSIS",
      items: [
        {
          name: "Past Proposals (Competition)",
          obtained: true,
          source: "AI Web Research",
        },
        {
          name: "List of competitors for this opportunity",
          obtained: true,
          source: "AI Web Research",
        },
        {
          name: "Competitor staffing information",
          obtained: false,
          source: "",
        },
        {
          name: "Competitor resumes and past performance",
          obtained: false,
          source: "",
        },
      ],
    },
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [selectedDocuments],
  );

  const handleFiles = (files: FileList) => {
    if (selectedDocuments.length === 0) {
      toast({
        title: "Select document category first",
        description:
          "Please select which documents you're uploading from the checklist.",
        variant: "destructive",
      });
      return;
    }

    Array.from(files).forEach((file) => {
      const newFile: UploadedFile = {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        category: selectedDocuments[0], // For demo, use first selected category
        status: "uploading",
      };

      setUploadedFiles((prev) => [...prev, newFile]);

      // Simulate upload
      setTimeout(() => {
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === newFile.id ? { ...f, status: "completed" } : f,
          ),
        );
        toast({
          title: "File uploaded successfully",
          description: `${file.name} has been processed and analyzed.`,
        });
      }, 2000);
    });
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleWebsiteSubmit = () => {
    if (websiteLink && selectedDocuments.length > 0) {
      const newFile: UploadedFile = {
        id: Math.random().toString(36).substr(2, 9),
        name: `Website: ${websiteLink}`,
        size: 0,
        type: "website",
        category: selectedDocuments[0],
        status: "uploading",
      };

      setUploadedFiles((prev) => [...prev, newFile]);
      setWebsiteLink("");

      setTimeout(() => {
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === newFile.id ? { ...f, status: "completed" } : f,
          ),
        );
        toast({
          title: "Website content extracted",
          description: "Information from the website has been analyzed.",
        });
      }, 3000);
    }
  };

  const handleTextSubmit = () => {
    if (pastedText && selectedDocuments.length > 0) {
      const newFile: UploadedFile = {
        id: Math.random().toString(36).substr(2, 9),
        name: `Text Content (${pastedText.substring(0, 30)}...)`,
        size: pastedText.length,
        type: "text",
        category: selectedDocuments[0],
        status: "uploading",
      };

      setUploadedFiles((prev) => [...prev, newFile]);
      setPastedText("");

      setTimeout(() => {
        setUploadedFiles((prev) =>
          prev.map((f) =>
            f.id === newFile.id ? { ...f, status: "completed" } : f,
          ),
        );
        toast({
          title: "Text content processed",
          description: "Pasted text has been analyzed and categorized.",
        });
      }, 1500);
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const toggleDocument = (document: string) => {
    setSelectedDocuments((prev) =>
      prev.includes(document)
        ? prev.filter((d) => d !== document)
        : [...prev, document],
    );
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Document Categories Checklist */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {Object.entries(documentCategories).map(([key, category]) => (
          <Card key={key} className="border-2">
            <CardHeader>
              <CardTitle className="text-lg">{category.title}</CardTitle>
              <CardDescription>
                Select documents you're uploading from this category
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {category.items.map((item, index) => (
                  <div
                    key={index}
                    className={`flex items-start space-x-3 p-2 rounded ${
                      item.obtained ? "bg-green-50 border border-green-200" : ""
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id={`${key}-${index}`}
                        checked={
                          selectedDocuments.includes(item.name) || item.obtained
                        }
                        onCheckedChange={() =>
                          !item.obtained && toggleDocument(item.name)
                        }
                        className="mt-1"
                        disabled={item.obtained}
                      />
                      {item.obtained && (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <Label
                        htmlFor={`${key}-${index}`}
                        className={`text-sm leading-5 ${item.obtained ? "cursor-default" : "cursor-pointer"}`}
                      >
                        {item.name}
                      </Label>
                      {item.obtained && (
                        <div className="text-xs text-green-600 mt-1">
                          ✓ Obtained via {item.source}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Upload Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* File Upload */}
        <Card className="border-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Upload className="h-5 w-5 text-blue-600" />
              <span>Upload Files</span>
            </CardTitle>
            <CardDescription>
              Drag & drop files or click to browse. Supports PDF, DOC, TXT,
              Images, Audio
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-300 hover:border-blue-400"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium mb-2">Drop files here</p>
              <p className="text-sm text-gray-500 mb-4">
                or click to browse files
              </p>
              <input
                type="file"
                multiple
                onChange={handleFileInput}
                className="hidden"
                id="file-upload"
                accept=".pdf,.doc,.docx,.txt,.md,.mp3,.png,.jpg,.jpeg"
              />
              <Label htmlFor="file-upload">
                <Button variant="outline" className="cursor-pointer">
                  <FileText className="h-4 w-4 mr-2" />
                  Browse Files
                </Button>
              </Label>
            </div>
          </CardContent>
        </Card>

        {/* Website Link */}
        <Card className="border-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <LinkIcon className="h-5 w-5 text-green-600" />
              <span>Website Link</span>
            </CardTitle>
            <CardDescription>
              Add website URLs for content extraction and analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="website-link">Website URL</Label>
                <Input
                  id="website-link"
                  type="url"
                  placeholder="https://example.com"
                  value={websiteLink}
                  onChange={(e) => setWebsiteLink(e.target.value)}
                />
              </div>
              <Button
                onClick={handleWebsiteSubmit}
                disabled={!websiteLink || selectedDocuments.length === 0}
                className="w-full"
                variant="outline"
              >
                <LinkIcon className="h-4 w-4 mr-2" />
                Extract Content
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Paste Text */}
        <Card className="border-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Type className="h-5 w-5 text-purple-600" />
              <span>Paste Text</span>
            </CardTitle>
            <CardDescription>
              Paste text content directly for analysis and processing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="paste-text">Text Content</Label>
                <Textarea
                  id="paste-text"
                  placeholder="Paste your text content here..."
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  rows={4}
                />
              </div>
              <Button
                onClick={handleTextSubmit}
                disabled={!pastedText || selectedDocuments.length === 0}
                className="w-full"
                variant="outline"
              >
                <Type className="h-4 w-4 mr-2" />
                Process Text
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <Card className="border-2">
          <CardHeader>
            <CardTitle>Uploaded Files</CardTitle>
            <CardDescription>
              Files uploaded and processed by AI for proposal generation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedFiles.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div>
                      {file.status === "completed" && (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      )}
                      {file.status === "uploading" && (
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
                      )}
                      {file.status === "error" && (
                        <AlertCircle className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-sm">{file.name}</p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(file.size)} • {file.category}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge
                      variant="outline"
                      className={
                        file.status === "completed"
                          ? "bg-green-50 text-green-700"
                          : file.status === "uploading"
                            ? "bg-blue-50 text-blue-700"
                            : "bg-red-50 text-red-700"
                      }
                    >
                      {file.status}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Processing Status */}
      <Card className="border-2 bg-blue-50">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-3">
            <div className="animate-pulse w-3 h-3 bg-blue-600 rounded-full"></div>
            <div>
              <p className="font-medium text-blue-900">AI Processing Active</p>
              <p className="text-sm text-blue-700">
                Documents are being analyzed and information extracted for
                proposal generation. Results will appear in the Plan tab.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
