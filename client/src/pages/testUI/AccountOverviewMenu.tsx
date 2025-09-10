import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  SquaresFour,
  UsersThree,
  AddressBook,
  Briefcase,
  ChartLineUp,
  Note,
  Money,
  Crosshair,
} from "phosphor-react";

const tabs = [
  { label: "Overview", icon: SquaresFour },
  { label: "Contacts", icon: AddressBook },
  { label: "Team", icon: UsersThree },
  { label: "Opportunities", icon: Crosshair },
  { label: "Experience", icon: Briefcase },
  { label: "Performance", icon: ChartLineUp },
  { label: "Notes", icon: Note },
  { label: "Financial", icon: Money },
];

const AccountOverviewMenu: React.FC = () => {
  const [activeTab, setActiveTab] = useState("Overview");

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-8 gap-2 mb-4 border-2 border-gray-300 p-2 rounded-xl">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.label;
        return (
          <Button
            key={tab.label}
            onClick={() => setActiveTab(tab.label)}
            variant="outline"
            className={`flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm w-full ${
              isActive
                ? "bg-gray-900 text-white border-gray-900"
                : "border border-gray-200 text-gray-900 hover:bg-gray-100"
            }`}
          >
            <tab.icon size={16} />
            {tab.label}
          </Button>
        );
      })}
    </div>
  );
};

export default AccountOverviewMenu;
