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
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Edit3,
  CheckCircle,
  AlertTriangle,
  Lock,
  Unlock,
  ChevronDown,
  ChevronRight,
  Sparkles,
  FileCheck,
  Scale,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ProposalSection {
  id: string;
  name: string;
  content: string;
  isLocked: boolean;
  isCompliant: boolean;
  score: number;
  suggestions: string[];
  wordCount: number;
  pageCount: number;
  pageLimit?: number;
}

export default function DetailRefineTab() {
  const { toast } = useToast();
  const [sections, setSections] = useState<ProposalSection[]>([
    {
      id: "executive-summary",
      name: "Executive Summary",
      content:
        "Megapolis Advisory brings unparalleled expertise in urban transit planning to the Metro Transit Expansion project. Our team has successfully delivered over 50 transit projects exceeding $100M in value, with a proven track record of on-time, on-budget delivery.\n\nOur approach leverages cutting-edge AI-powered traffic modeling, sustainable design principles, and extensive stakeholder engagement to ensure project success. We understand the City of Springfield's commitment to environmental sustainability and will integrate green infrastructure throughout the project.\n\nKey differentiators include our proprietary transit optimization algorithms, local partnerships with minority-owned businesses, and our team's 200+ combined years of transit experience.",
      isLocked: false,
      isCompliant: true,
      score: 85,
      suggestions: [
        "Add specific metrics about project outcomes",
        "Include client testimonial or reference",
        "Highlight unique technological advantages",
      ],
      wordCount: 156,
      pageCount: 2,
      pageLimit: 4,
    },
    {
      id: "qualifications",
      name: "Qualifications",
      content:
        "Megapolis Advisory has been at the forefront of transportation infrastructure development for over two decades. Our portfolio includes:\n\n• Metro Rail System, Denver: $2.4B project delivered 6 months ahead of schedule\n• Bus Rapid Transit, Portland: Award-winning sustainable design\n• Multimodal Hub, Austin: Integrated 5 transportation modes\n\nOur team holds over 50 professional engineering licenses across 12 states, with specialized certifications in transit planning, environmental assessment, and project management. We maintain partnerships with leading technology providers and have developed proprietary tools for traffic simulation and route optimization.",
      isLocked: false,
      isCompliant: false,
      score: 78,
      suggestions: [
        "Add specific team member qualifications",
        "Include more recent project examples",
        "Address RFP's minimum experience requirements",
        "Add professional certifications details",
      ],
      wordCount: 132,
      pageCount: 5,
      pageLimit: 8,
    },
    {
      id: "technical-approach",
      name: "Technical Approach",
      content:
        "Our technical approach combines proven methodologies with innovative solutions:\n\nPhase 1: Comprehensive Analysis\n- Traffic pattern analysis using AI-powered modeling\n- Environmental impact assessment\n- Stakeholder engagement and community input\n\nPhase 2: Design Development\n- Sustainable infrastructure design\n- Integration with existing transportation networks\n- Smart city technology implementation\n\nPhase 3: Implementation\n- Phased construction to minimize disruption\n- Real-time monitoring and quality control\n- Community communication and updates\n\nOur approach prioritizes sustainability, community engagement, and technological innovation while ensuring compliance with all federal and state regulations.",
      isLocked: true,
      isCompliant: true,
      score: 92,
      suggestions: [],
      wordCount: 167,
      pageCount: 8,
      pageLimit: 12,
    },
  ]);

  const [contractExceptions, setContractExceptions] = useState([
    {
      id: 1,
      clause: "Liquidated Damages (Section 15.3)",
      issue: "Daily penalty rate exceeds industry standard",
      recommendation: "Request cap at 5% of contract value",
      accepted: false,
    },
    {
      id: 2,
      clause: "Intellectual Property (Section 8.2)",
      issue: "Broad IP assignment to client",
      recommendation: "Limit to project-specific developments only",
      accepted: true,
    },
    {
      id: 3,
      clause: "Insurance Requirements (Section 12.1)",
      issue: "Professional liability coverage amount",
      recommendation: "Standard $2M coverage instead of $5M",
      accepted: false,
    },
  ]);

  const [overallScore, setOverallScore] = useState(85);

  const handleContentChange = (sectionId: string, newContent: string) => {
    setSections((prev) =>
      prev.map((section) =>
        section.id === sectionId
          ? {
              ...section,
              content: newContent,
              wordCount: newContent.split(/\s+/).length,
            }
          : section,
      ),
    );
  };

  const toggleLock = (sectionId: string) => {
    setSections((prev) =>
      prev.map((section) =>
        section.id === sectionId
          ? { ...section, isLocked: !section.isLocked }
          : section,
      ),
    );
    toast({
      title: "Section updated",
      description: `Section ${sections.find((s) => s.id === sectionId)?.isLocked ? "unlocked" : "locked"} successfully.`,
    });
  };

  const handleAISuggestion = (sectionId: string, suggestion: string) => {
    toast({
      title: "AI Suggestion Applied",
      description: `Applied suggestion: ${suggestion}`,
    });
  };

  const handleExceptionToggle = (exceptionId: number) => {
    setContractExceptions((prev) =>
      prev.map((ex) =>
        ex.id === exceptionId ? { ...ex, accepted: !ex.accepted } : ex,
      ),
    );
  };

  return (
    <div className="space-y-6">
      {/* Proposal Score Overview */}
      <Card className="border-2 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileCheck className="h-5 w-5 text-blue-600" />
            <span>Proposal Compliance & Score</span>
          </CardTitle>
          <CardDescription>
            Overall proposal assessment based on RFP criteria
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {overallScore}%
              </div>
              <p className="text-sm text-gray-600">Overall Score</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {sections.filter((s) => s.isCompliant).length}
              </div>
              <p className="text-sm text-gray-600">Compliant Sections</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {sections.filter((s) => !s.isCompliant).length}
              </div>
              <p className="text-sm text-gray-600">Need Attention</p>
            </div>
          </div>
          <Progress value={overallScore} className="mt-4" />
        </CardContent>
      </Card>

      {/* Section Review */}
      <div className="space-y-4">
        {sections.map((section) => (
          <Card key={section.id} className="border-2">
            <Collapsible>
              <CollapsibleTrigger asChild>
                <CardHeader className="cursor-pointer hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <ChevronRight className="h-5 w-5" />
                      <div>
                        <CardTitle className="text-lg">
                          {section.name}
                        </CardTitle>
                        <CardDescription>
                          {section.wordCount} words • {section.pageCount} pages
                          {section.pageLimit && ` (max ${section.pageLimit})`}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge
                        variant="outline"
                        className={
                          section.isCompliant
                            ? "bg-green-50 text-green-700"
                            : "bg-red-50 text-red-700"
                        }
                      >
                        {section.isCompliant ? (
                          <CheckCircle className="h-3 w-3 mr-1" />
                        ) : (
                          <AlertTriangle className="h-3 w-3 mr-1" />
                        )}
                        {section.isCompliant ? "Compliant" : "Issues"}
                      </Badge>
                      <Badge variant="outline" className="bg-blue-50">
                        Score: {section.score}%
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleLock(section.id);
                        }}
                      >
                        {section.isLocked ? (
                          <Lock className="h-4 w-4 text-red-600" />
                        ) : (
                          <Unlock className="h-4 w-4 text-green-600" />
                        )}
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <CardContent className="space-y-4">
                  {/* Content Editor */}
                  <div>
                    <Textarea
                      value={section.content}
                      onChange={(e) =>
                        handleContentChange(section.id, e.target.value)
                      }
                      disabled={section.isLocked}
                      rows={8}
                      className="font-mono text-sm"
                    />
                  </div>

                  {/* AI Suggestions */}
                  {section.suggestions.length > 0 && (
                    <Card className="bg-yellow-50 border-yellow-200">
                      <CardHeader>
                        <CardTitle className="text-sm flex items-center space-x-2">
                          <Sparkles className="h-4 w-4 text-yellow-600" />
                          <span>AI Suggestions for Improvement</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {section.suggestions.map((suggestion, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-2 bg-white rounded border"
                            >
                              <span className="text-sm">{suggestion}</span>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() =>
                                  handleAISuggestion(section.id, suggestion)
                                }
                              >
                                Apply
                              </Button>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Section Actions */}
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline">
                      <Edit3 className="h-4 w-4 mr-2" />
                      Edit Layout
                    </Button>
                    <Button size="sm" variant="outline">
                      <Sparkles className="h-4 w-4 mr-2" />
                      AI Enhance
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => toggleLock(section.id)}
                    >
                      {section.isLocked ? (
                        <>
                          <Unlock className="h-4 w-4 mr-2" />
                          Unlock
                        </>
                      ) : (
                        <>
                          <Lock className="h-4 w-4 mr-2" />
                          Lock
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </CollapsibleContent>
            </Collapsible>
          </Card>
        ))}
      </div>

      {/* Contract Exceptions */}
      <Card className="border-2 border-orange-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Scale className="h-5 w-5 text-orange-600" />
            <span>Contract Exceptions & Legal Review</span>
          </CardTitle>
          <CardDescription>
            AI-identified contract issues and recommended exceptions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {contractExceptions.map((exception) => (
              <Card key={exception.id} className="border">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-sm mb-1">
                        {exception.clause}
                      </h4>
                      <p className="text-sm text-red-600 mb-2">
                        <strong>Issue:</strong> {exception.issue}
                      </p>
                      <p className="text-sm text-green-600">
                        <strong>Recommendation:</strong>{" "}
                        {exception.recommendation}
                      </p>
                    </div>
                    <div className="ml-4">
                      <Button
                        size="sm"
                        variant={exception.accepted ? "default" : "outline"}
                        onClick={() => handleExceptionToggle(exception.id)}
                      >
                        {exception.accepted ? "Accepted" : "Accept"}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="mt-6 p-4 bg-orange-50 rounded-lg">
            <p className="text-sm text-orange-700">
              <strong>Legal Review Status:</strong> 2 of 3 exceptions accepted.
              Review remaining items with legal counsel before final submission.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Compliance Summary */}
      <Card className="border-2 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-6 w-6 text-green-600" />
            <div>
              <p className="font-medium text-green-900">
                Proposal Ready for Next Phase
              </p>
              <p className="text-sm text-green-700">
                All sections reviewed and compliance issues addressed. Ready to
                proceed to Layout/Print tab.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
