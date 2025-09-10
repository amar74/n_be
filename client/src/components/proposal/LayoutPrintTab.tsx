import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Layout,
  Printer,
  Download,
  Eye,
  CheckCircle,
  AlertTriangle,
  Mail,
  FileText,
  Package,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ProposalPage {
  id: string;
  section: string;
  pageNumber: number;
  title: string;
  preview: string;
  isCompliant: boolean;
  issues?: string[];
}

export default function LayoutPrintTab() {
  const { toast } = useToast();
  const [selectedPages, setSelectedPages] = useState<string[]>([]);
  const [printOptions, setPrintOptions] = useState({
    format: "digital",
    copies: 3,
    binding: "spiral",
    paper: "standard",
    doubleSided: true,
  });

  const proposalPages: ProposalPage[] = [
    {
      id: "cover",
      section: "Cover",
      pageNumber: 1,
      title: "Metro Transit Expansion Proposal",
      preview: "📄",
      isCompliant: true,
    },
    {
      id: "toc",
      section: "Table of Contents",
      pageNumber: 2,
      title: "Contents",
      preview: "📋",
      isCompliant: true,
    },
    {
      id: "letter-1",
      section: "Letter",
      pageNumber: 3,
      title: "Transmittal Letter - Page 1",
      preview: "✉️",
      isCompliant: true,
    },
    {
      id: "letter-2",
      section: "Letter",
      pageNumber: 4,
      title: "Transmittal Letter - Page 2",
      preview: "✉️",
      isCompliant: true,
    },
    {
      id: "exec-1",
      section: "Executive Summary",
      pageNumber: 5,
      title: "Executive Summary - Page 1",
      preview: "📊",
      isCompliant: true,
    },
    {
      id: "exec-2",
      section: "Executive Summary",
      pageNumber: 6,
      title: "Executive Summary - Page 2",
      preview: "📊",
      isCompliant: false,
      issues: ["Footer formatting inconsistent", "Page number alignment"],
    },
    {
      id: "qual-1",
      section: "Qualifications",
      pageNumber: 7,
      title: "Qualifications - Team Overview",
      preview: "👥",
      isCompliant: true,
    },
    {
      id: "qual-2",
      section: "Qualifications",
      pageNumber: 8,
      title: "Qualifications - Project Experience",
      preview: "🏗️",
      isCompliant: true,
    },
    {
      id: "tech-1",
      section: "Technical Approach",
      pageNumber: 9,
      title: "Technical Approach - Phase 1",
      preview: "⚙️",
      isCompliant: true,
    },
    {
      id: "tech-2",
      section: "Technical Approach",
      pageNumber: 10,
      title: "Technical Approach - Implementation",
      preview: "🔧",
      isCompliant: true,
    },
  ];

  const sectionSummary = [
    { section: "Cover & Contents", pages: 2, compliant: true },
    { section: "Letter", pages: 2, compliant: true },
    { section: "Executive Summary", pages: 2, compliant: false },
    { section: "Qualifications", pages: 2, compliant: true },
    { section: "Technical Approach", pages: 2, compliant: true },
  ];

  const totalPages = proposalPages.length;
  const compliantPages = proposalPages.filter((p) => p.isCompliant).length;

  const handlePageSelect = (pageId: string) => {
    setSelectedPages((prev) =>
      prev.includes(pageId)
        ? prev.filter((id) => id !== pageId)
        : [...prev, pageId],
    );
  };

  const handleSelectAll = () => {
    if (selectedPages.length === proposalPages.length) {
      setSelectedPages([]);
    } else {
      setSelectedPages(proposalPages.map((p) => p.id));
    }
  };

  const handlePreview = () => {
    toast({
      title: "Generating Preview",
      description: "Creating full proposal preview...",
    });
  };

  const handlePrint = () => {
    toast({
      title: "Print Job Started",
      description: `Printing ${selectedPages.length} pages with ${printOptions.binding} binding.`,
    });
  };

  const handleExport = (format: string) => {
    toast({
      title: `Exporting to ${format.toUpperCase()}`,
      description: "Your proposal is being exported...",
    });
  };

  return (
    <div className="space-y-6">
      {/* Compliance Overview */}
      <Card className="border-2 bg-gradient-to-r from-blue-50 to-green-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Layout className="h-5 w-5 text-blue-600" />
            <span>Proposal Layout Compliance</span>
          </CardTitle>
          <CardDescription>
            Final review of proposal formatting and compliance status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {totalPages}
              </div>
              <p className="text-sm text-gray-600">Total Pages</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {compliantPages}
              </div>
              <p className="text-sm text-gray-600">Compliant</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {totalPages - compliantPages}
              </div>
              <p className="text-sm text-gray-600">Need Review</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {Math.round((compliantPages / totalPages) * 100)}%
              </div>
              <p className="text-sm text-gray-600">Compliance</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section Summary */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle>Section Summary</CardTitle>
          <CardDescription>
            Overview of proposal sections and their compliance status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {sectionSummary.map((section, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <h4 className="font-medium">{section.section}</h4>
                  <p className="text-sm text-gray-600">{section.pages} pages</p>
                </div>
                <Badge
                  variant="outline"
                  className={
                    section.compliant
                      ? "bg-green-50 text-green-700"
                      : "bg-red-50 text-red-700"
                  }
                >
                  {section.compliant ? (
                    <CheckCircle className="h-3 w-3 mr-1" />
                  ) : (
                    <AlertTriangle className="h-3 w-3 mr-1" />
                  )}
                  {section.compliant ? "Compliant" : "Issues"}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Page Layout Grid */}
      <Card className="border-2">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Page Layout Preview</CardTitle>
              <CardDescription>
                Review individual pages and select for printing
              </CardDescription>
            </div>
            <div className="space-x-2">
              <Button variant="outline" size="sm" onClick={handleSelectAll}>
                {selectedPages.length === proposalPages.length
                  ? "Deselect All"
                  : "Select All"}
              </Button>
              <Button size="sm" onClick={handlePreview}>
                <Eye className="h-4 w-4 mr-2" />
                Preview All
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {proposalPages.map((page) => (
              <Card
                key={page.id}
                className={`cursor-pointer border-2 transition-all ${
                  selectedPages.includes(page.id)
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300"
                } ${!page.isCompliant ? "border-orange-300" : ""}`}
                onClick={() => handlePageSelect(page.id)}
              >
                <CardContent className="p-3 text-center">
                  <div className="relative">
                    <div className="text-3xl mb-2">{page.preview}</div>
                    {!page.isCompliant && (
                      <AlertTriangle className="absolute -top-1 -right-1 h-4 w-4 text-orange-500" />
                    )}
                  </div>
                  <div className="text-xs font-medium mb-1">
                    Page {page.pageNumber}
                  </div>
                  <div className="text-xs text-gray-600 truncate">
                    {page.title}
                  </div>
                  {page.issues && (
                    <div className="mt-2">
                      <Badge
                        variant="outline"
                        className="bg-orange-50 text-orange-700 text-xs"
                      >
                        Issues
                      </Badge>
                    </div>
                  )}
                  <div className="mt-2">
                    <Checkbox
                      checked={selectedPages.includes(page.id)}
                      onChange={() => handlePageSelect(page.id)}
                    />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Print Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Printer className="h-5 w-5 text-blue-600" />
              <span>Print Configuration</span>
            </CardTitle>
            <CardDescription>
              Configure printing options for physical submission
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm font-medium">Output Format</Label>
              <Select
                value={printOptions.format}
                onValueChange={(value) =>
                  setPrintOptions((prev) => ({ ...prev, format: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="digital">Digital Only</SelectItem>
                  <SelectItem value="print">Physical Print</SelectItem>
                  <SelectItem value="both">Digital + Print</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Number of Copies</Label>
              <Select
                value={printOptions.copies.toString()}
                onValueChange={(value) =>
                  setPrintOptions((prev) => ({
                    ...prev,
                    copies: parseInt(value),
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 Copy</SelectItem>
                  <SelectItem value="3">3 Copies</SelectItem>
                  <SelectItem value="5">5 Copies</SelectItem>
                  <SelectItem value="10">10 Copies</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Binding Type</Label>
              <Select
                value={printOptions.binding}
                onValueChange={(value) =>
                  setPrintOptions((prev) => ({ ...prev, binding: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="spiral">Spiral Binding</SelectItem>
                  <SelectItem value="comb">Comb Binding</SelectItem>
                  <SelectItem value="three-ring">3-Ring Binder</SelectItem>
                  <SelectItem value="perfect">Perfect Binding</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Paper Type</Label>
              <Select
                value={printOptions.paper}
                onValueChange={(value) =>
                  setPrintOptions((prev) => ({ ...prev, paper: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="standard">Standard Paper</SelectItem>
                  <SelectItem value="recycled">Recycled Paper</SelectItem>
                  <SelectItem value="premium">Premium Paper</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="double-sided"
                checked={printOptions.doubleSided}
                onCheckedChange={(checked) =>
                  setPrintOptions((prev) => ({
                    ...prev,
                    doubleSided: checked as boolean,
                  }))
                }
              />
              <Label htmlFor="double-sided" className="text-sm">
                Double-sided printing
              </Label>
            </div>
          </CardContent>
        </Card>

        <Card className="border-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Package className="h-5 w-5 text-green-600" />
              <span>Submission Options</span>
            </CardTitle>
            <CardDescription>
              Choose how to submit your completed proposal
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              className="w-full justify-start"
              variant="outline"
              onClick={() => handleExport("pdf")}
            >
              <Download className="h-4 w-4 mr-2" />
              Export as PDF
            </Button>

            <Button
              className="w-full justify-start"
              variant="outline"
              onClick={() => handleExport("docx")}
            >
              <FileText className="h-4 w-4 mr-2" />
              Export as Word Document
            </Button>

            <Button
              className="w-full justify-start"
              variant="outline"
              onClick={() =>
                toast({
                  title: "Email Prepared",
                  description: "Email with proposal attachment is ready.",
                })
              }
            >
              <Mail className="h-4 w-4 mr-2" />
              Email to Client
            </Button>

            <Button
              className="w-full justify-start"
              variant="outline"
              onClick={handlePrint}
              disabled={selectedPages.length === 0}
            >
              <Printer className="h-4 w-4 mr-2" />
              Print Selected Pages ({selectedPages.length})
            </Button>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-700">
                <strong>Submission Deadline:</strong> December 15, 2024 at 3:00
                PM
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Hand delivery to: City Hall, Room 215
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Final Status */}
      <Card className="border-2 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-6 w-6 text-green-600" />
            <div>
              <p className="font-medium text-green-900">
                Proposal Ready for Submission
              </p>
              <p className="text-sm text-green-700">
                Layout review complete. {compliantPages} of {totalPages} pages
                are compliant. Ready for final submission.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
