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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  Users,
  FileText,
  Presentation,
  Send,
  Phone,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ScheduleItem {
  id: string;
  task: string;
  category: "pre-rfp" | "post-rfp";
  startDate: string;
  endDate: string;
  assignee: string;
  status: "completed" | "in-progress" | "pending" | "overdue";
  progress: number;
  dependencies?: string[];
}

interface ReviewMilestone {
  id: string;
  name: string;
  type: "pink" | "red" | "final";
  date: string;
  participants: string[];
  status: "scheduled" | "completed" | "pending";
}

export default function ScheduleTab() {
  const { toast } = useToast();
  const [rfpReleaseDate, setRfpReleaseDate] = useState("2024-11-01");
  const [submissionDate, setSubmissionDate] = useState("2024-12-15");
  const [selectedPhase, setSelectedPhase] = useState<
    "pre-rfp" | "post-rfp" | "both"
  >("both");

  const scheduleItems: ScheduleItem[] = [
    // Pre-RFP Phase
    {
      id: "1",
      task: "RFI/SOI issued",
      category: "pre-rfp",
      startDate: "2024-09-15",
      endDate: "2024-09-15",
      assignee: "Client",
      status: "completed",
      progress: 100,
    },
    {
      id: "2",
      task: "Initial market research",
      category: "pre-rfp",
      startDate: "2024-09-16",
      endDate: "2024-09-30",
      assignee: "Research Team",
      status: "completed",
      progress: 100,
    },
    {
      id: "3",
      task: "Team assembly and role definition",
      category: "pre-rfp",
      startDate: "2024-10-01",
      endDate: "2024-10-15",
      assignee: "Project Manager",
      status: "completed",
      progress: 100,
    },
    {
      id: "4",
      task: "Client relationship building",
      category: "pre-rfp",
      startDate: "2024-10-01",
      endDate: "2024-10-31",
      assignee: "Business Development",
      status: "completed",
      progress: 100,
    },

    // Post-RFP Phase
    {
      id: "5",
      task: "RFP analysis and breakdown",
      category: "post-rfp",
      startDate: "2024-11-01",
      endDate: "2024-11-05",
      assignee: "Proposal Manager",
      status: "completed",
      progress: 100,
    },
    {
      id: "6",
      task: "Proposal kick-off meeting",
      category: "post-rfp",
      startDate: "2024-11-06",
      endDate: "2024-11-06",
      assignee: "All Team",
      status: "completed",
      progress: 100,
    },
    {
      id: "7",
      task: "Request information from subconsultants",
      category: "post-rfp",
      startDate: "2024-11-06",
      endDate: "2024-11-08",
      assignee: "Procurement",
      status: "completed",
      progress: 100,
    },
    {
      id: "8",
      task: "Site visit and technical assessment",
      category: "post-rfp",
      startDate: "2024-11-10",
      endDate: "2024-11-12",
      assignee: "Technical Team",
      status: "completed",
      progress: 100,
    },
    {
      id: "9",
      task: "Pre-proposal conference",
      category: "post-rfp",
      startDate: "2024-11-15",
      endDate: "2024-11-15",
      assignee: "Client",
      status: "completed",
      progress: 100,
    },
    {
      id: "10",
      task: "Finalize subconsultant selection",
      category: "post-rfp",
      startDate: "2024-11-16",
      endDate: "2024-11-20",
      assignee: "Procurement",
      status: "completed",
      progress: 100,
    },
    {
      id: "11",
      task: "Gather questions for client",
      category: "post-rfp",
      startDate: "2024-11-18",
      endDate: "2024-11-22",
      assignee: "Technical Team",
      status: "completed",
      progress: 100,
    },
    {
      id: "12",
      task: "Submit questions to client",
      category: "post-rfp",
      startDate: "2024-11-22",
      endDate: "2024-11-22",
      assignee: "Proposal Manager",
      status: "completed",
      progress: 100,
    },
    {
      id: "13",
      task: "Client answers posted",
      category: "post-rfp",
      startDate: "2024-11-29",
      endDate: "2024-11-29",
      assignee: "Client",
      status: "completed",
      progress: 100,
    },
    {
      id: "14",
      task: "Subconsultant information due",
      category: "post-rfp",
      startDate: "2024-11-25",
      endDate: "2024-11-30",
      assignee: "Subconsultants",
      status: "completed",
      progress: 100,
    },
    {
      id: "15",
      task: "Technical writing assignments due",
      category: "post-rfp",
      startDate: "2024-11-30",
      endDate: "2024-12-05",
      assignee: "Technical Writers",
      status: "in-progress",
      progress: 85,
    },
    {
      id: "16",
      task: "Pink team review",
      category: "post-rfp",
      startDate: "2024-12-06",
      endDate: "2024-12-07",
      assignee: "Review Team",
      status: "pending",
      progress: 0,
    },
    {
      id: "17",
      task: "Red team review",
      category: "post-rfp",
      startDate: "2024-12-09",
      endDate: "2024-12-10",
      assignee: "Review Team",
      status: "pending",
      progress: 0,
    },
    {
      id: "18",
      task: "Final changes and review",
      category: "post-rfp",
      startDate: "2024-12-11",
      endDate: "2024-12-13",
      assignee: "All Team",
      status: "pending",
      progress: 0,
    },
    {
      id: "19",
      task: "Print and production",
      category: "post-rfp",
      startDate: "2024-12-13",
      endDate: "2024-12-14",
      assignee: "Production Team",
      status: "pending",
      progress: 0,
    },
    {
      id: "20",
      task: "Proposal submission",
      category: "post-rfp",
      startDate: "2024-12-15",
      endDate: "2024-12-15",
      assignee: "Delivery Team",
      status: "pending",
      progress: 0,
    },
  ];

  const reviewMilestones: ReviewMilestone[] = [
    {
      id: "pink",
      name: "Pink Team Review",
      type: "pink",
      date: "2024-12-06",
      participants: ["Sarah Johnson", "Michael Chen", "Technical Team"],
      status: "scheduled",
    },
    {
      id: "red",
      name: "Red Team Review",
      type: "red",
      date: "2024-12-09",
      participants: ["Lisa Rodriguez", "External Reviewer", "Quality Team"],
      status: "pending",
    },
    {
      id: "final",
      name: "Final Review",
      type: "final",
      date: "2024-12-13",
      participants: ["Project Manager", "Principal", "Legal Review"],
      status: "pending",
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-50 text-green-700 border-green-300";
      case "in-progress":
        return "bg-blue-50 text-blue-700 border-blue-300";
      case "pending":
        return "bg-gray-50 text-gray-700 border-gray-300";
      case "overdue":
        return "bg-red-50 text-red-700 border-red-300";
      default:
        return "bg-gray-50 text-gray-700 border-gray-300";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4" />;
      case "in-progress":
        return <Clock className="h-4 w-4" />;
      case "overdue":
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <Calendar className="h-4 w-4" />;
    }
  };

  const filteredItems = scheduleItems.filter((item) => {
    if (selectedPhase === "both") return true;
    return item.category === selectedPhase;
  });

  const completedTasks = scheduleItems.filter(
    (item) => item.status === "completed",
  ).length;
  const totalTasks = scheduleItems.length;
  const overallProgress = Math.round((completedTasks / totalTasks) * 100);

  const handleUpdateDate = () => {
    toast({
      title: "Schedule Updated",
      description: "Dates updated and schedule recalculated.",
    });
  };

  return (
    <div className="space-y-6">
      {/* Schedule Overview */}
      <Card className="border-2 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-blue-600" />
            <span>Proposal Schedule Overview</span>
          </CardTitle>
          <CardDescription>
            Track progress and manage timeline for proposal development
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {overallProgress}%
              </div>
              <p className="text-sm text-gray-600">Overall Progress</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {completedTasks}
              </div>
              <p className="text-sm text-gray-600">Tasks Completed</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {totalTasks - completedTasks}
              </div>
              <p className="text-sm text-gray-600">Tasks Remaining</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {Math.ceil(
                  (new Date(submissionDate).getTime() - Date.now()) /
                    (1000 * 60 * 60 * 24),
                )}
              </div>
              <p className="text-sm text-gray-600">Days Until Due</p>
            </div>
          </div>
          <Progress value={overallProgress} className="mt-4" />
        </CardContent>
      </Card>

      {/* Date Configuration */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle>Key Dates Configuration</CardTitle>
          <CardDescription>
            Update critical dates to automatically adjust the schedule
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label className="text-sm font-medium">RFP Release Date</Label>
              <Input
                type="date"
                value={rfpReleaseDate}
                onChange={(e) => setRfpReleaseDate(e.target.value)}
              />
            </div>
            <div>
              <Label className="text-sm font-medium">Submission Date</Label>
              <Input
                type="date"
                value={submissionDate}
                onChange={(e) => setSubmissionDate(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button onClick={handleUpdateDate} className="w-full">
                Update Schedule
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Phase Filter */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle>Schedule Phases</CardTitle>
          <CardDescription>
            View different phases of the proposal development process
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select value={selectedPhase}>
            <SelectTrigger className="max-w-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="both">All Phases</SelectItem>
              <SelectItem value="pre-rfp">Pre-RFP Phase</SelectItem>
              <SelectItem value="post-rfp">Post-RFP Phase</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Review Milestones */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Presentation className="h-5 w-5 text-purple-600" />
            <span>Review Milestones</span>
          </CardTitle>
          <CardDescription>
            Critical review points in the proposal development
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {reviewMilestones.map((milestone) => (
              <Card key={milestone.id} className="border">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div
                        className={`p-2 rounded-full ${
                          milestone.type === "pink"
                            ? "bg-pink-100"
                            : milestone.type === "red"
                              ? "bg-red-100"
                              : "bg-purple-100"
                        }`}
                      >
                        <Presentation
                          className={`h-5 w-5 ${
                            milestone.type === "pink"
                              ? "text-pink-600"
                              : milestone.type === "red"
                                ? "text-red-600"
                                : "text-purple-600"
                          }`}
                        />
                      </div>
                      <div>
                        <h4 className="font-medium">{milestone.name}</h4>
                        <p className="text-sm text-gray-600">
                          {milestone.date}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Users className="h-3 w-3 text-gray-400" />
                          <span className="text-xs text-gray-500">
                            {milestone.participants.join(", ")}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Badge
                      variant="outline"
                      className={getStatusColor(milestone.status)}
                    >
                      {milestone.status === "scheduled" && (
                        <Calendar className="h-3 w-3 mr-1" />
                      )}
                      {milestone.status === "completed" && (
                        <CheckCircle className="h-3 w-3 mr-1" />
                      )}
                      {milestone.status === "pending" && (
                        <Clock className="h-3 w-3 mr-1" />
                      )}
                      {milestone.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Schedule Timeline */}
      <Card className="border-2">
        <CardHeader>
          <CardTitle>Detailed Schedule</CardTitle>
          <CardDescription>
            Complete timeline with all tasks and milestones
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredItems.map((item) => (
              <Card key={item.id} className="border">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3 flex-1">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(item.status)}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{item.task}</h4>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                          <span>
                            {item.startDate} - {item.endDate}
                          </span>
                          <span className="flex items-center space-x-1">
                            <Users className="h-3 w-3" />
                            <span>{item.assignee}</span>
                          </span>
                        </div>
                        {item.status === "in-progress" && (
                          <Progress
                            value={item.progress}
                            className="mt-2 h-2"
                          />
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge
                        variant="outline"
                        className={`text-xs ${
                          item.category === "pre-rfp"
                            ? "bg-blue-50 text-blue-700"
                            : "bg-purple-50 text-purple-700"
                        }`}
                      >
                        {item.category === "pre-rfp" ? "Pre-RFP" : "Post-RFP"}
                      </Badge>
                      <Badge
                        variant="outline"
                        className={getStatusColor(item.status)}
                      >
                        {item.status}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card className="border-2 bg-blue-50">
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" size="sm" className="justify-start">
              <FileText className="h-4 w-4 mr-2" />
              Export Schedule
            </Button>
            <Button variant="outline" size="sm" className="justify-start">
              <Send className="h-4 w-4 mr-2" />
              Share Timeline
            </Button>
            <Button variant="outline" size="sm" className="justify-start">
              <Phone className="h-4 w-4 mr-2" />
              Schedule Review
            </Button>
            <Button variant="outline" size="sm" className="justify-start">
              <Calendar className="h-4 w-4 mr-2" />
              Add Milestone
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
