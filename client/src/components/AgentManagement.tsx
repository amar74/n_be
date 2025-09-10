import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Plus,
  Bot,
  Sparkles,
  CheckCircle,
  X,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Agent {
  id: string;
  name: string;
  type: string;
  status: "active" | "idle";
  tasks: string[];
  modules: string[];
  lastActive: string;
  tasksCompleted: number;
  avatar: string;
  capabilities: string[];
  autonomyLevel: string;
}

interface AgentManagementProps {
  moduleContext?: string;
}

export default function AgentManagement({ moduleContext = "General" }: AgentManagementProps) {
  const { toast } = useToast();
  
  const [agentPanelOpen, setAgentPanelOpen] = useState(false);
  const [createAgentOpen, setCreateAgentOpen] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: "agent-001",
      name: "Account Analyst Pro",
      type: "Account Management",
      status: "active",
      tasks: ["Monitor account health", "Generate insights", "Update contact info"],
      modules: ["accounts", "opportunities"],
      lastActive: "2 minutes ago",
      tasksCompleted: 147,
      avatar: "🤖",
      capabilities: ["Data Analysis", "Report Generation", "Contact Management"],
      autonomyLevel: "High"
    },
    {
      id: "agent-002",
      name: "Survey Coordinator",
      type: "Client Engagement",
      status: "active",
      tasks: ["Schedule surveys", "Follow up responses", "Generate reports"],
      modules: ["client-surveys", "accounts"],
      lastActive: "5 minutes ago",
      tasksCompleted: 89,
      avatar: "📊",
      capabilities: ["Survey Management", "Client Communication", "Analytics"],
      autonomyLevel: "Medium"
    },
    {
      id: "agent-003",
      name: "Opportunity Hunter",
      type: "Business Development",
      status: "idle",
      tasks: ["Research new opportunities", "Qualify leads", "Update pipeline"],
      modules: ["opportunities", "accounts"],
      lastActive: "1 hour ago",
      tasksCompleted: 234,
      avatar: "🎯",
      capabilities: ["Lead Generation", "Market Research", "Pipeline Management"],
      autonomyLevel: "High"
    }
  ]);

  const [newAgent, setNewAgent] = useState({
    name: "",
    type: "",
    modules: [] as string[],
    tasks: [] as string[],
    capabilities: [] as string[],
    autonomyLevel: "Medium",
    avatar: "🤖"
  });

  const [newTask, setNewTask] = useState("");
  const [newCapability, setNewCapability] = useState("");

  const createAgent = () => {
    if (!newAgent.name || !newAgent.type) {
      toast({
        title: "Missing Information",
        description: "Please provide agent name and type",
        variant: "destructive",
      });
      return;
    }

    const agent: Agent = {
      id: `agent-${Date.now()}`,
      name: newAgent.name,
      type: newAgent.type,
      status: "idle",
      tasks: newAgent.tasks,
      modules: newAgent.modules,
      lastActive: "Just created",
      tasksCompleted: 0,
      avatar: newAgent.avatar,
      capabilities: newAgent.capabilities,
      autonomyLevel: newAgent.autonomyLevel
    };

    setAgents([...agents, agent]);
    setNewAgent({
      name: "",
      type: "",
      modules: [],
      tasks: [],
      capabilities: [],
      autonomyLevel: "Medium",
      avatar: "🤖"
    });
    setCreateAgentOpen(false);
    toast({
      title: "Agent Created",
      description: `${agent.name} has been successfully created`,
    });
  };

  const activateAgent = (agentId: string) => {
    setAgents(agents.map(agent =>
      agent.id === agentId ? { ...agent, status: "active" as const, lastActive: "Just activated" } : agent
    ));
    toast({
      title: "Agent Activated",
      description: "Agent is now active and processing tasks",
    });
  };

  const deactivateAgent = (agentId: string) => {
    setAgents(agents.map(agent =>
      agent.id === agentId ? { ...agent, status: "idle" as const, lastActive: "Just paused" } : agent
    ));
    toast({
      title: "Agent Paused",
      description: "Agent has been paused",
    });
  };

  const deleteAgent = (agentId: string) => {
    setAgents(agents.filter(agent => agent.id !== agentId));
    toast({
      title: "Agent Deleted",
      description: "Agent has been permanently removed",
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 border-green-200";
      case "idle":
        return "bg-gray-100 text-gray-800 border-gray-200";
      default:
        return "bg-blue-100 text-blue-800 border-blue-200";
    }
  };

  const addTask = () => {
    if (newTask.trim()) {
      setNewAgent({ ...newAgent, tasks: [...newAgent.tasks, newTask.trim()] });
      setNewTask("");
    }
  };

  const removeTask = (index: number) => {
    setNewAgent({
      ...newAgent,
      tasks: newAgent.tasks.filter((_, i) => i !== index)
    });
  };

  const addCapability = () => {
    if (newCapability.trim()) {
      setNewAgent({ ...newAgent, capabilities: [...newAgent.capabilities, newCapability.trim()] });
      setNewCapability("");
    }
  };

  const removeCapability = (index: number) => {
    setNewAgent({
      ...newAgent,
      capabilities: newAgent.capabilities.filter((_, i) => i !== index)
    });
  };

  const toggleModule = (module: string) => {
    const updatedModules = newAgent.modules.includes(module)
      ? newAgent.modules.filter(m => m !== module)
      : [...newAgent.modules, module];
    setNewAgent({ ...newAgent, modules: updatedModules });
  };

  return (
    <>
      {/* Floating Agent Management Button */}
      <div className="fixed top-20 right-20 z-50">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
              onClick={() => setAgentPanelOpen(true)}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full p-3 shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105"
              >
                <Bot className="h-6 w-6" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>AI Agent Management</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
          {agents.filter(a => a.status === "active").length}
        </div>
      </div>

      {/* Agent Management Panel */}
      <Dialog open={agentPanelOpen} onOpenChange={setAgentPanelOpen}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3 text-2xl">
              <Bot className="h-7 w-7 text-purple-600" />
              AI Agent Management System
              {moduleContext && <Badge variant="outline">{moduleContext}</Badge>}
            </DialogTitle>
            <DialogDescription>
              Create and manage AI agents to automate tasks across all modules
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {agents.filter(a => a.status === "active").length}
                  </div>
                  <div className="text-sm text-green-700">Active Agents</div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {agents.reduce((sum, agent) => sum + agent.tasksCompleted, 0)}
                  </div>
                  <div className="text-sm text-blue-700">Tasks Completed</div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-r from-purple-50 to-violet-50 border-purple-200">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-purple-600">{agents.length}</div>
                  <div className="text-sm text-purple-700">Total Agents</div>
                </CardContent>
              </Card>
              <Card className="bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200">
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {agents.filter(a => a.status === "idle").length}
                  </div>
                  <div className="text-sm text-orange-700">Idle Agents</div>
                </CardContent>
              </Card>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Your AI Agents</h3>
              <Button
                onClick={() => setCreateAgentOpen(true)}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create New Agent
              </Button>
            </div>

            {/* Agents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {agents.map((agent) => (
                <Card
                  key={agent.id}
                  className="border-2 hover:border-purple-300 transition-all duration-200 hover:shadow-lg"
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">{agent.avatar}</div>
                        <div>
                          <h4 className="font-semibold text-lg">{agent.name}</h4>
                          <p className="text-sm text-gray-600">{agent.type}</p>
                        </div>
                      </div>
                      <Badge className={getStatusColor(agent.status)}>
                        {agent.status}
                      </Badge>
                    </div>

                    <div className="space-y-3 mb-4">
                      <div>
                        <p className="text-sm font-medium text-gray-700">Modules:</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {agent.modules.map((module, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {module}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-sm font-medium text-gray-700">Capabilities:</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {agent.capabilities.map((cap, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs bg-blue-50">
                              {cap}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-sm font-medium text-gray-700">Current Tasks:</p>
                        <ul className="text-xs text-gray-600 mt-1">
                          {agent.tasks.slice(0, 2).map((task, idx) => (
                            <li key={idx} className="flex items-center gap-1">
                              <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
                              {task}
                            </li>
                          ))}
                          {agent.tasks.length > 2 && (
                            <li className="text-purple-600">+{agent.tasks.length - 2} more</li>
                          )}
                        </ul>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t">
                      <div className="text-xs text-gray-500">
                        <p>Completed: {agent.tasksCompleted} tasks</p>
                        <p>Last active: {agent.lastActive}</p>
                      </div>
                      <div className="flex gap-2">
                        {agent.status === "idle" ? (
                          <Button
                            size="sm"
                            onClick={() => activateAgent(agent.id)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            Activate
                          </Button>
                        ) : (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => deactivateAgent(agent.id)}
                          >
                            Pause
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => deleteAgent(agent.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Create Agent Dialog */}
      <Dialog open={createAgentOpen} onOpenChange={setCreateAgentOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              Create New AI Agent
            </DialogTitle>
            <DialogDescription>
              Configure a new AI agent to automate tasks across your modules
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="agent-name">Agent Name</Label>
                <Input
                  id="agent-name"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  placeholder="Enter agent name"
                />
              </div>
              <div>
                <Label htmlFor="agent-type">Agent Type</Label>
                <Select
                  value={newAgent.type}
                  onValueChange={(value) => setNewAgent({ ...newAgent, type: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select agent type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Account Management">Account Management</SelectItem>
                    <SelectItem value="Business Development">Business Development</SelectItem>
                    <SelectItem value="Client Engagement">Client Engagement</SelectItem>
                    <SelectItem value="Project Management">Project Management</SelectItem>
                    <SelectItem value="Data Analysis">Data Analysis</SelectItem>
                    <SelectItem value="Report Generation">Report Generation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="agent-avatar">Agent Avatar</Label>
              <Select
                value={newAgent.avatar}
                onValueChange={(value) => setNewAgent({ ...newAgent, avatar: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select avatar" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="🤖">🤖 Robot</SelectItem>
                  <SelectItem value="🎯">🎯 Target</SelectItem>
                  <SelectItem value="📊">📊 Chart</SelectItem>
                  <SelectItem value="⚡">⚡ Lightning</SelectItem>
                  <SelectItem value="🔍">🔍 Search</SelectItem>
                  <SelectItem value="💼">💼 Briefcase</SelectItem>
                  <SelectItem value="🧠">🧠 Brain</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Modules</Label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {["accounts", "opportunities", "client-surveys", "proposals", "projects", "reports"].map((module) => (
                  <div key={module} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={module}
                      checked={newAgent.modules.includes(module)}
                      onChange={() => toggleModule(module)}
                      className="rounded"
                    />
                    <Label htmlFor={module} className="text-sm capitalize">
                      {module.replace("-", " ")}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <Label>Tasks</Label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <Input
                    value={newTask}
                    onChange={(e) => setNewTask(e.target.value)}
                    placeholder="Add a task"
                    onKeyPress={(e) => e.key === "Enter" && addTask()}
                  />
                  <Button onClick={addTask} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-1">
                  {newAgent.tasks.map((task, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs">
                      {task}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeTask(idx)}
                        className="ml-1 h-4 w-4 p-0"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <Label>Capabilities</Label>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <Input
                    value={newCapability}
                    onChange={(e) => setNewCapability(e.target.value)}
                    placeholder="Add a capability"
                    onKeyPress={(e) => e.key === "Enter" && addCapability()}
                  />
                  <Button onClick={addCapability} size="sm">
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-1">
                  {newAgent.capabilities.map((cap, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs bg-blue-50">
                      {cap}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeCapability(idx)}
                        className="ml-1 h-4 w-4 p-0"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="autonomy-level">Autonomy Level</Label>
              <Select
                value={newAgent.autonomyLevel}
                onValueChange={(value) => setNewAgent({ ...newAgent, autonomyLevel: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select autonomy level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Low">Low - Requires approval for all actions</SelectItem>
                  <SelectItem value="Medium">Medium - Requires approval for major actions</SelectItem>
                  <SelectItem value="High">High - Can act independently</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setCreateAgentOpen(false)}>
                Cancel
              </Button>
              <Button onClick={createAgent} className="bg-purple-600 hover:bg-purple-700">
                <CheckCircle className="h-4 w-4 mr-2" />
                Create Agent
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
