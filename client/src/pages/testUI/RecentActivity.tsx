import React from "react";
import { Card, CardContent } from "@/components/ui/card";

const activities = [
  {
    text: "Proposal submitted for metro transit expansion",
    time: "2 days ago",
    color: "bg-green-500",
  },
  {
    text: "Meeting with Sarah Johnson scheduled",
    time: "1 week ago",
    color: "bg-blue-500",
  },
  {
    text: "Contract amendment signed",
    time: "2 weeks ago",
    color: "bg-purple-500",
  },
];

const RecentActivity: React.FC = () => {
  return (
    <Card className="bg-white rounded-2xl border border-gray-200 shadow-sm">
      <CardContent className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Activity
        </h2>
        <ul className="divide-y divide-[#EAEAEA]">
          {activities.map((item, idx) => (
            <li
              key={idx}
              className={`flex items-start gap-3 py-3 ${
                idx < activities.length - 1 ? "border-b border-[#EAEAEA]" : ""
              }`}
            >
              <span
                className={`w-3 h-3 rounded-full mt-1.5 ${item.color}`}
              ></span>
              <div>
                <p className="text-sm font-medium text-gray-800">
                  {item.text}
                </p>
                <p className="text-xs text-gray-500">{item.time}</p>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
};

export default RecentActivity;
