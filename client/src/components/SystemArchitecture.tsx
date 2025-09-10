import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ArchitectureNodeProps {
  title: string;
  icon: string;
  description?: string;
  color: string;
  size?: "sm" | "md" | "lg";
}

const ArchitectureNode: React.FC<ArchitectureNodeProps> = ({
  title,
  icon,
  description,
  color,
  size = "md",
}) => {
  const sizeClasses = {
    sm: "p-3 min-h-[80px]",
    md: "p-4 min-h-[100px]",
    lg: "p-6 min-h-[120px]",
  };

  return (
    <Card
      className={`${sizeClasses[size]} border-2 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105`}
      style={{ borderColor: color }}
    >
      <CardContent className="p-0 h-full flex flex-col items-center justify-center text-center">
        <div className="text-2xl mb-2">{icon}</div>
        <h3 className="font-semibold text-sm leading-tight">{title}</h3>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
};

const ConnectionLine: React.FC<{
  direction: "horizontal" | "vertical";
  className?: string;
}> = ({ direction, className = "" }) => (
  <div
    className={`bg-gradient-to-r from-blue-400 to-purple-500 ${
      direction === "horizontal" ? "h-0.5 w-full" : "w-0.5 h-full"
    } ${className}`}
  />
);

export default function SystemArchitecture() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            System Architecture
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Microservices architecture with modern cloud-native components and
            AI-powered document processing
          </p>
        </div>

        {/* Architecture Diagram */}
        <div className="space-y-8">
          {/* User & External Layer */}
          <div className="text-center">
            <Badge
              variant="outline"
              className="mb-4 bg-emerald-50 text-emerald-700 border-emerald-300"
            >
              User & External
            </Badge>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-md mx-auto">
              <ArchitectureNode
                title="User (Browser)"
                icon="👨‍💻"
                color="#10b981"
                size="md"
              />
              <ArchitectureNode
                title="Marketing Website"
                icon="🌐"
                color="#10b981"
                size="md"
              />
            </div>
          </div>

          {/* Connection */}
          <div className="flex justify-center">
            <ConnectionLine direction="vertical" className="h-8" />
          </div>

          {/* Network & Gateway Layer */}
          <div className="text-center">
            <Badge
              variant="outline"
              className="mb-4 bg-blue-50 text-blue-700 border-blue-300"
            >
              Network & Gateway
            </Badge>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-md mx-auto">
              <ArchitectureNode
                title="CDN"
                icon="📡"
                description="CloudFront"
                color="#3b82f6"
                size="md"
              />
              <ArchitectureNode
                title="API Gateway"
                icon="🔐"
                color="#3b82f6"
                size="md"
              />
            </div>
          </div>

          {/* Connection */}
          <div className="flex justify-center">
            <ConnectionLine direction="vertical" className="h-8" />
          </div>

          {/* Application Services Layer */}
          <div className="text-center">
            <Badge
              variant="outline"
              className="mb-4 bg-purple-50 text-purple-700 border-purple-300"
            >
              Application Services (Microservices)
            </Badge>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              <ArchitectureNode
                title="Auth Service"
                icon="🔑"
                color="#8b5cf6"
                size="sm"
              />
              <ArchitectureNode
                title="Proposal Mgmt Service"
                icon="📝"
                color="#8b5cf6"
                size="sm"
              />
              <ArchitectureNode
                title="Billing Service"
                icon="💳"
                color="#8b5cf6"
                size="sm"
              />
              <ArchitectureNode
                title="Document & AI Service"
                icon="🤖"
                color="#8b5cf6"
                size="sm"
              />
              <ArchitectureNode
                title="Notification Service"
                icon="✉️"
                color="#8b5cf6"
                size="sm"
              />
            </div>
          </div>

          {/* Connection */}
          <div className="flex justify-center">
            <ConnectionLine direction="vertical" className="h-8" />
          </div>

          {/* Data & File Stores Layer */}
          <div className="text-center">
            <Badge
              variant="outline"
              className="mb-4 bg-orange-50 text-orange-700 border-orange-300"
            >
              Data & File Stores
            </Badge>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <ArchitectureNode
                title="Relational DB"
                icon="🗄️"
                description="PostgreSQL"
                color="#f97316"
                size="md"
              />
              <ArchitectureNode
                title="Vector DB"
                icon="🧠"
                description="Pinecone/Weaviate"
                color="#f97316"
                size="md"
              />
              <ArchitectureNode
                title="Object Storage"
                icon="📦"
                description="AWS S3"
                color="#f97316"
                size="md"
              />
            </div>
          </div>

          {/* Third-Party APIs Layer */}
          <div className="text-center mt-12">
            <Badge
              variant="outline"
              className="mb-4 bg-red-50 text-red-700 border-red-300"
            >
              Third-Party APIs
            </Badge>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-md mx-auto">
              <ArchitectureNode
                title="Stripe API"
                icon="💲"
                color="#ef4444"
                size="md"
              />
              <ArchitectureNode
                title="LLM API"
                icon="✨"
                description="OpenAI/Google"
                color="#ef4444"
                size="md"
              />
            </div>
          </div>
        </div>

        {/* Data Flow Information */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <h3 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
              <span>🔄</span> Data Flow
            </h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• User requests via CDN</li>
              <li>• API Gateway routes to services</li>
              <li>• Services process and store data</li>
            </ul>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <h3 className="font-semibold text-purple-800 mb-3 flex items-center gap-2">
              <span>🚀</span> Features
            </h3>
            <ul className="text-sm text-purple-700 space-y-1">
              <li>• AI-powered document processing</li>
              <li>• Microservices architecture</li>
              <li>• Real-time notifications</li>
            </ul>
          </Card>

          <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <h3 className="font-semibold text-green-800 mb-3 flex items-center gap-2">
              <span>🛡️</span> Security
            </h3>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• API Gateway authentication</li>
              <li>• Service-to-service security</li>
              <li>• Data encryption at rest</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
