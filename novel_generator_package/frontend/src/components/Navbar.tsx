import React from 'react';
import { Bell, User } from 'lucide-react';

const Navbar: React.FC = () => {
  return (
    <header className="bg-white shadow-sm">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center">
          <h2 className="text-lg font-medium text-gray-800">自动小说生成器</h2>
        </div>
        <div className="flex items-center space-x-4">
          <button className="p-1 rounded-full text-gray-500 hover:bg-gray-100">
            <Bell className="h-5 w-5" />
          </button>
          <div className="relative">
            <button className="flex items-center text-sm rounded-full focus:outline-none">
              <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                <User className="h-5 w-5 text-gray-500" />
              </div>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
