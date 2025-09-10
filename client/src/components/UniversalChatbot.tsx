import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  MessageCircle,
  Send,
  Bot,
  User,
  Minimize2,
  Maximize2,
  X,
  Lightbulb,
  HelpCircle,
  Sparkles,
  Clock,
  CheckCircle,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  timestamp: Date;
  module?: string;
}

interface ChatbotProps {
  currentModule?: string;
}

const QUICK_ACTIONS = [
  "How do I create a new account?",
  "What's the status of my proposals?",
  "Show me project deadlines",
  "How to track opportunities?",
  "Generate a report",
  "Help with KPIs",
];

const MODULE_CONTEXT = {
  "Accounts": "account management, client relationships, contact information, account health scores",
  "Opportunities": "business opportunities, pipeline management, lead tracking, opportunity stages",
  "Proposals": "proposal creation, submission tracking, proposal templates, win rates",
  "Projects": "project management, timelines, deliverables, project status tracking",
  "Client Surveys": "survey creation, response collection, client feedback, survey analytics",
  "Campaigns": "marketing campaigns, campaign performance, audience targeting, campaign analytics",
  "Interviews": "interview scheduling, candidate management, interview feedback, hiring process",
  "KPIs": "key performance indicators, metrics tracking, performance analytics, reporting",
  "Finance": "financial tracking, budget management, revenue analysis, cost tracking",
  "Resources": "resource allocation, team management, utilization rates, resource planning",
  "Dashboard": "overview metrics, summary statistics, quick access to all modules"
};

export default function UniversalChatbot({ currentModule = "General" }: ChatbotProps) {
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      type: "bot",
      content: `Hello! I'm your intelligent assistant for Megapolis Technologies. I can help you with any questions about ${currentModule === "General" ? "all modules" : currentModule} or any other part of the system. What would you like to know?`,
      timestamp: new Date(),
      module: currentModule
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateBotResponse = (userMessage: string): string => {
    const message = userMessage.toLowerCase();
    
    // Module-specific responses
    if (message.includes("account") || message.includes("client")) {
      return "I can help you with account management! You can create new accounts by clicking the 'Add New Account' button, view client details including health scores and contact information, track communication history, and manage MSA status. Would you like me to guide you through any specific account-related task?";
    }
    
    if (message.includes("opportunity") || message.includes("lead") || message.includes("pipeline")) {
      return "For opportunities, you can track your sales pipeline, manage lead stages, view opportunity values and probabilities, set follow-up reminders, and generate pipeline reports. I can help you navigate to specific opportunities or explain how to update opportunity stages. What specific aspect of opportunity management interests you?";
    }
    
    if (message.includes("proposal")) {
      return "Regarding proposals, you can create new proposals using templates, track submission status, monitor win rates, collaborate with team members, and manage proposal deadlines. I can walk you through the proposal creation process or help you find specific proposals. What would you like to do with proposals?";
    }
    
    if (message.includes("project")) {
      return "For project management, you can view project timelines, track deliverables, monitor project health, assign team members, and generate progress reports. I can help you navigate to specific projects or explain how to update project status. What project information do you need?";
    }
    
    if (message.includes("survey")) {
      return "With client surveys, you can create custom surveys, distribute them to clients, collect responses, analyze feedback data, and generate survey reports. I can guide you through survey creation or help you interpret survey results. What survey task can I assist with?";
    }
    
    if (message.includes("campaign")) {
      return "For campaigns, you can create marketing campaigns, track performance metrics, manage target audiences, monitor engagement rates, and analyze ROI. I can help you set up new campaigns or review existing campaign performance. What campaign activity interests you?";
    }
    
    if (message.includes("interview")) {
      return "Regarding interviews, you can schedule candidate interviews, manage interview feedback, track hiring progress, coordinate with team members, and generate hiring reports. I can help you navigate the interview process or find specific candidate information. What interview task do you need help with?";
    }
    
    if (message.includes("kpi") || message.includes("metric") || message.includes("performance")) {
      return "For KPIs and metrics, you can track key performance indicators, generate performance reports, set up automated alerts, compare trends over time, and create custom dashboards. I can help you understand specific metrics or guide you to relevant reports. Which KPIs would you like to explore?";
    }
    
    if (message.includes("finance") || message.includes("budget") || message.includes("revenue")) {
      return "Regarding finance, you can track revenue, manage budgets, monitor expenses, generate financial reports, analyze profitability, and set financial goals. I can help you navigate financial data or explain specific financial metrics. What financial information do you need?";
    }
    
    if (message.includes("resource") || message.includes("team") || message.includes("staff")) {
      return "For resources, you can manage team allocation, track utilization rates, plan capacity, assign staff to projects, and generate resource reports. I can help you find available resources or optimize team assignments. What resource management task can I assist with?";
    }
    
    // General help responses
    if (message.includes("help") || message.includes("how")) {
      return `I'm here to help you navigate Megapolis Technologies! Since you're currently in the ${currentModule} module, I can provide specific guidance for ${MODULE_CONTEXT[currentModule as keyof typeof MODULE_CONTEXT] || "this area"}. I can also answer questions about any other module. Try asking me specific questions like "How do I create a new account?" or "Show me project deadlines."`;
    }
    
    if (message.includes("report") || message.includes("export")) {
      return "I can help you generate various reports! Most modules have export capabilities - look for download buttons or 'Generate Report' options. You can create account summaries, opportunity pipelines, project status reports, financial statements, and more. Which type of report are you looking to create?";
    }
    
    if (message.includes("create") || message.includes("new") || message.includes("add")) {
      return "To create new items, look for the '+' or 'Add New' buttons in each module. Each module has specific creation workflows - accounts, opportunities, proposals, projects, surveys, and more. I can guide you through the creation process for any specific item type. What would you like to create?";
    }
    
    if (message.includes("status") || message.includes("update")) {
      return "You can check and update status information throughout the system. Each module displays current status with color-coded indicators. Use the edit buttons or status dropdowns to make updates. I can help you find specific status information or guide you through updating processes. What status do you need to check or update?";
    }
    
    if (message.includes("search") || message.includes("find")) {
      return "You can search across all modules using the search functionality in each section. Use filters to narrow down results by date, status, type, or other criteria. I can help you locate specific items or guide you to the right search tools. What are you trying to find?";
    }
    
    if (message.includes("dashboard") || message.includes("overview")) {
      return "The dashboard provides a comprehensive overview of all your activities. You can see key metrics, quick access to modules, recent activities, and performance indicators. Each module also has its own dashboard view. Would you like me to explain any specific dashboard metrics or help you navigate to particular information?";
    }
    
    // Default responses for unclear questions
    const defaultResponses = [
      `Great question! Since you're in the ${currentModule} module, I can provide specific guidance for ${MODULE_CONTEXT[currentModule as keyof typeof MODULE_CONTEXT] || "this area"}. Could you be more specific about what you'd like to know?`,
      "I'm here to help with any questions about Megapolis Technologies! You can ask me about accounts, opportunities, proposals, projects, surveys, campaigns, interviews, KPIs, finance, resources, or general navigation. What specific topic interests you?",
      "I can assist with various tasks across all modules. Try asking me about specific features like 'How to create an account?' or 'Show me proposal templates' or 'What are my project deadlines?' What would you like to explore?",
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
      module: currentModule
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Simulate typing delay
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: generateBotResponse(inputValue),
        timestamp: new Date(),
        module: currentModule
      };

      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 1000 + Math.random() * 1000);
  };

  const handleQuickAction = (action: string) => {
    setInputValue(action);
    handleSendMessage();
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome",
        type: "bot",
        content: `Hello! I'm your intelligent assistant for Megapolis Technologies. I can help you with any questions about ${currentModule === "General" ? "all modules" : currentModule} or any other part of the system. What would you like to know?`,
        timestamp: new Date(),
        module: currentModule
      }
    ]);
    toast({
      title: "Chat Cleared",
      description: "Conversation history has been reset",
    });
  };

  return (
    <>
      {/* Floating Chat Button */}
      <div className="fixed top-20 right-6 z-50">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                onClick={() => setIsOpen(true)}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-full p-3 shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105"
              >
                <MessageCircle className="h-6 w-6" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>AI Assistant - Ask me anything!</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        {messages.length > 1 && (
          <div className="absolute -top-2 -right-2 bg-emerald-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
            {messages.length - 1}
          </div>
        )}
      </div>

      {/* Chat Dialog */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className={`${isMinimized ? 'max-w-sm' : 'max-w-2xl'} transition-all duration-300`}>
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-3">
                <Bot className="h-6 w-6 text-emerald-600" />
                AI Assistant
                {currentModule && <Badge variant="outline" className="text-xs">{currentModule}</Badge>}
              </DialogTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMinimized(!isMinimized)}
                >
                  {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearChat}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <DialogDescription>
              Your intelligent assistant for all Megapolis Technologies modules
            </DialogDescription>
          </DialogHeader>

          {!isMinimized && (
            <div className="space-y-4">
              {/* Quick Actions */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  Quick Questions
                </h4>
                <div className="flex flex-wrap gap-2">
                  {QUICK_ACTIONS.map((action, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickAction(action)}
                      className="text-xs"
                    >
                      {action}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Chat Messages */}
              <Card className="h-96 flex flex-col">
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      {message.type === 'bot' && (
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                            <Bot className="h-4 w-4 text-emerald-600" />
                          </div>
                        </div>
                      )}
                      
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {formatTime(message.timestamp)}
                        </p>
                      </div>

                      {message.type === 'user' && (
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="h-4 w-4 text-blue-600" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}

                  {isTyping && (
                    <div className="flex gap-3 justify-start">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center">
                          <Bot className="h-4 w-4 text-emerald-600" />
                        </div>
                      </div>
                      <div className="bg-gray-100 rounded-lg px-4 py-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </CardContent>

                {/* Message Input */}
                <div className="border-t p-4">
                  <div className="flex gap-2">
                    <Input
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      placeholder="Ask me anything about Megapolis Technologies..."
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputValue.trim() || isTyping}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>

              {/* Help Footer */}
              <div className="text-center">
                <p className="text-xs text-gray-500 flex items-center justify-center gap-1">
                  <HelpCircle className="h-3 w-3" />
                  I can help with accounts, opportunities, proposals, projects, and more!
                </p>
              </div>
            </div>
          )}

          {isMinimized && (
            <div className="text-center py-4">
              <p className="text-sm text-gray-600">Chat minimized - click to expand</p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
