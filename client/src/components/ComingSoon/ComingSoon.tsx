import { memo } from 'react';
import { 
  Target, 
  Building2, 
  FileText, 
  Users, 
  FileCheck, 
  Calendar, 
  Calculator, 
  ShoppingCart, 
  BarChart3,
  Clock,
  Sparkles
} from 'lucide-react';
import { ComingSoonProps } from './ComingSoon.types';

const MODULE_ICONS = {
  opportunities: Target,
  accounts: Building2,
  proposals: FileText,
  resources: Users,
  contracts: FileCheck,
  projects: Calendar,
  finance: Calculator,
  procurement: ShoppingCart,
  kpis: BarChart3,
} as const;

const MODULE_DESCRIPTIONS = {
  opportunities: "Track and manage business opportunities, leads, and potential deals with comprehensive pipeline management.",
  accounts: "Manage your client accounts, relationships, and business information in one centralized location.",
  proposals: "Create, manage, and track business proposals with templates, approval workflows, and analytics.",
  resources: "Manage team members, contractors, and resource allocation across projects and departments.",
  contracts: "Handle contract lifecycle management, renewals, compliance tracking, and document storage.",
  projects: "Plan, execute, and monitor projects with timeline management, task tracking, and team collaboration.",
  finance: "Comprehensive financial management including budgeting, invoicing, expense tracking, and reporting.",
  procurement: "Streamline procurement processes, vendor management, purchase orders, and supply chain operations.",
  kpis: "Monitor key performance indicators, generate reports, and track business metrics with interactive dashboards.",
} as const;

const COMING_FEATURES = {
  opportunities: ["Lead scoring and qualification", "Pipeline analytics", "Automated follow-ups", "Integration with CRM"],
  accounts: ["Account health scoring", "Relationship mapping", "Revenue forecasting", "Custom fields"],
  proposals: ["Template library", "E-signature integration", "Approval workflows", "Win/loss analytics"],
  resources: ["Skill matrix management", "Capacity planning", "Performance tracking", "Time logging"],
  contracts: ["Automated renewals", "Compliance monitoring", "Risk assessment", "Digital signatures"],
  projects: ["Gantt charts", "Resource allocation", "Budget tracking", "Milestone management"],
  finance: ["Advanced reporting", "Cash flow forecasting", "Multi-currency support", "Tax management"],
  procurement: ["Vendor scorecards", "Automated approvals", "Inventory management", "Cost analytics"],
  kpis: ["Custom dashboards", "Real-time alerts", "Benchmark comparisons", "Predictive analytics"],
} as const;

function ComingSoon({ moduleId, moduleName }: ComingSoonProps) {
  const IconComponent = MODULE_ICONS[moduleId as keyof typeof MODULE_ICONS] || Building2;
  const description = MODULE_DESCRIPTIONS[moduleId as keyof typeof MODULE_DESCRIPTIONS] || "This module is currently under development.";
  const features = COMING_FEATURES[moduleId as keyof typeof COMING_FEATURES] || [];

  return (
    <div className="w-full h-full font-inter bg-[#F5F3F2] min-h-[calc(100vh-120px)]">
      <div className="flex flex-col items-center justify-center min-h-[600px] px-6 py-12">
        {/* Main Content Container */}
        <div className="max-w-2xl mx-auto text-center space-y-8">
          {/* Icon and Status */}
          <div className="flex flex-col items-center space-y-4">
            <div className="relative">
              <div className="w-24 h-24 bg-white rounded-2xl shadow-lg flex items-center justify-center">
                <IconComponent className="w-12 h-12 text-[#0f0901]" />
              </div>
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                <Clock className="w-4 h-4 text-white" />
              </div>
            </div>
            
            <div className="flex items-center space-x-2 px-4 py-2 bg-orange-100 rounded-full">
              <Sparkles className="w-4 h-4 text-orange-600" />
              <span className="text-orange-600 font-medium text-sm">Coming Soon</span>
            </div>
          </div>

          {/* Title and Description */}
          <div className="space-y-4">
            <h1 className="text-4xl font-bold text-[#0f0901]">
              {moduleName}
            </h1>
            <p className="text-lg text-gray-600 leading-relaxed">
              {description}
            </p>
          </div>

          {/* Features Preview */}
          {features.length > 0 && (
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
              <h3 className="text-xl font-semibold text-[#0f0901] mb-6">
                What's Coming
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {features.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="w-2 h-2 bg-orange-500 rounded-full flex-shrink-0"></div>
                    <span className="text-gray-700 text-sm">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Call to Action */}
          <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-2xl p-8 border border-orange-200">
            <h3 className="text-lg font-semibold text-[#0f0901] mb-2">
              Stay Tuned!
            </h3>
            <p className="text-gray-600 mb-4">
              We're working hard to bring you this module. In the meantime, explore our other features.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button 
                onClick={() => window.history.back()}
                className="px-6 py-3 bg-white text-[#0f0901] rounded-lg font-medium border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                Go Back
              </button>
              <button 
                onClick={() => window.location.href = '/module/accounts'}
                className="px-6 py-3 bg-[#0f0901] text-white rounded-lg font-medium hover:bg-gray-800 transition-colors"
              >
                Explore Accounts
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(ComingSoon);
