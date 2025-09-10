import React from "react";
import {
  Clock,
  CurrencyCircleDollar,
  Star,
  Users,
  CheckCircle,
} from "phosphor-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";

const PastPerformanceCard: React.FC = () => {
  const metrics = [
    {
      icon: Clock,
      value: "95%",
      label: "On-Time Delivery",
    },
    {
      icon: CurrencyCircleDollar,
      value: "98%",
      label: "Budget Compliance",
    },
    {
      icon: Star,
      value: "4.8/5.0",
      label: "Client Satisfaction",
    },
    {
      icon: Users,
      value: "85%",
      label: "Repeat Client Rate",
    },
    {
      icon: CheckCircle,
      value: "24",
      label: "Safety Record",
      subLabel: "month zero incidents",
    },
  ];

  return (
    <Card className="rounded-2xl border border-gray-200 shadow-sm mt-6 bg-white">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-bold text-gray-900">
          Past Performance
        </CardTitle>
        <p className="text-sm text-gray-500">
          Performance metrics and client satisfaction
        </p>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
          {metrics.map((metric, idx) => {
            const Icon = metric.icon;
            return (
              <div
                key={idx}
                className="p-4 py-6 rounded-xl border border-[#0F0901]"
              >
                {/* Icon inside circle */}
                <div className="w-12 h-12 rounded-full bg-[#F3F3F3] flex items-center justify-center mb-4 border border-[#E6E6E6]">
                  <Icon size={22} weight="fill" className="text-orange-400" />
                </div>

                {/* Value and SubLabel */}
                <p className="text-xl font-bold text-gray-900">
                  {metric.value}
                  {metric.subLabel && (
                    <span className="text-xs text-gray-900 font-semibold">
                      {" "}
                      {metric.subLabel}
                    </span>
                  )}
                </p>

                {/* Label */}
                <p className="text-xs font-semibold mt-1 text-[#9C9C9C]">{metric.label}</p>

                
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default PastPerformanceCard;
