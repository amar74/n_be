import React from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { MagnifyingGlass, Bell, List } from 'phosphor-react';
import logo from '@/assets/logo.png';
import john from '@/assets/john.png';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  return (
    <header className="px-6 py-4 flex items-center justify-between relative z-10" style={{ backgroundColor: '#F5F3F2' }}>
      {/* Left side - Logo and menu button */}
      <div className="flex items-center space-x-4">
        <button 
          onClick={onMenuClick}
          className="lg:hidden p-1 text-gray-600 hover:text-gray-800"
        >
          <List size={20} />
        </button>
        
        <img src={logo} alt="Logo" className="w-36 h-10" />
      </div>

      {/* Center - Search bar */}
      <div className="flex-1 max-w-md mx-8">
        <div className="relative">
          <MagnifyingGlass className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-800" size={16} />
          <input
            type="text"
            placeholder="Search accounts..."
            className="w-full pl-10 pr-4 py-2 border-[1px] border-gray-500 rounded-full bg-white text-sm focus:outline-none "
          />
        </div>
      </div>

      {/* Right side - Notifications and user */}
      <div className="flex items-center space-x-4 ">
        <button className=" text-gray-600  hover:text-gray-800 relative bg-[#f8f7f6]  rounded-full p-3">
          <Bell  size={20} />
          <span className="absolute -top-0 -right-0 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        
        <div className="flex items-center gap-3">
          <Avatar className="w-10 h-10">
            <AvatarImage src={john} alt="John Doe" />
            <AvatarFallback className="bg-orange-500 text-white text-sm">JD</AvatarFallback>
          </Avatar>
          <div className="hidden md:block">
            <div className="text-sm font-medium text-gray-900">John Doe</div>
            <div className="text-xs text-gray-500">john330@gmail.com</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;