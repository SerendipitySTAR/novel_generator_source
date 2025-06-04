import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Home, Settings } from 'lucide-react';

const Sidebar: React.FC = () => {
  return (
    <div className="w-64 bg-white shadow-md flex flex-col h-full">
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold text-gray-800">自动小说生成器</h1>
        <p className="text-sm text-gray-500">AI驱动的创作助手</p>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <Link
              to="/"
              className="flex items-center p-2 text-gray-700 rounded hover:bg-gray-100"
            >
              <Home className="mr-3 h-5 w-5" />
              <span>首页</span>
            </Link>
          </li>
          <li>
            <Link
              to="/projects"
              className="flex items-center p-2 text-gray-700 rounded hover:bg-gray-100"
            >
              <BookOpen className="mr-3 h-5 w-5" />
              <span>我的项目</span>
            </Link>
          </li>
          <li>
            <Link
              to="/settings"
              className="flex items-center p-2 text-gray-700 rounded hover:bg-gray-100"
            >
              <Settings className="mr-3 h-5 w-5" />
              <span>设置</span>
            </Link>
          </li>
        </ul>
      </nav>
      <div className="p-4 border-t">
        <p className="text-xs text-gray-500">© 2025 自动小说生成器</p>
      </div>
    </div>
  );
};

export default Sidebar;
