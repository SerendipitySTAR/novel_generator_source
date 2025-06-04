import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-16 flex flex-col items-center">
      <h1 className="text-4xl font-bold text-gray-800 mb-4">404 - 页面未找到</h1>
      <p className="text-xl text-gray-600 mb-8">您访问的页面不存在或已被移除</p>
      <Link
        to="/"
        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
      >
        返回首页
      </Link>
    </div>
  );
};

export default NotFoundPage;
