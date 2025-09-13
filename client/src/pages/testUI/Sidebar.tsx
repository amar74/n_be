import React, { useState } from "react";
import {
  Target,
  Users,
  FileText,
  BookOpen,
  ShoppingCart,
  ChartBar,
  SignOut,
  CurrencyCircleDollar,
  Kanban,
  X,
} from "phosphor-react";
import { FilePen } from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navigationItems = [
  { icon: Target, label: "Opportunities" },
  { icon: Users, label: "Accounts" },
  { icon: FileText, label: "Proposals" },
  { icon: BookOpen, label: "Resources" },
  { icon: FilePen, label: "Contracts" },
  { icon: Kanban, label: "Projects" },
  { icon: CurrencyCircleDollar, label: "Finance" },
  { icon: ShoppingCart, label: "Procurements" },
  { icon: ChartBar, label: "KPIs" },
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const [activeItem, setActiveItem] = useState("Accounts");

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
        fixed lg:static top-0 bottom-0 left-0 z-30 w-64 bg-white border-r-0 border-t-0 rounded-tr-2xl border-gray-200 
        transform ${isOpen ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 
        transition-transform duration-300 ease-in-out flex flex-col
      `}
      >
        {/* Close button for mobile */}
        <div className="flex items-center justify-end p-4 lg:hidden">
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6">
          <ul className="space-y-1">
            {navigationItems.map((item, index) => {
              const isActive = activeItem === item.label;
              return (
                <li key={index}>
                  <button
                    onClick={() => setActiveItem(item.label)}
                    className={`
                      w-full flex items-center space-x-3 px-3 py-2.5 mb-2.5 text-left
                      ${
                        isActive
                          ? "text-black border-b-2 border-gray-900 "
                          : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
                      }
                    `}
                  >
                    <item.icon
                      size={18}
                      className={isActive ? "text-black" : ""}
                      weight="fill"
                    />
                    <span className="text-sm font-medium">{item.label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Logout */}
        <div className="p-4 border-gray-200">
          <button className="w-full flex items-center space-x-3 px-3 py-10 text-black rounded-lg transition-colors">
            <SignOut size={18} weight="bold" className="text-black" />
            <span className="text-sm font-medium">Log-out</span>
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
