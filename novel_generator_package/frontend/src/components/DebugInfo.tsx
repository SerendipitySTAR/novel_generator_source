import React, { useState } from 'react';

interface DebugInfoProps {
  data: any;
  title: string;
}

const DebugInfo: React.FC<DebugInfoProps> = ({ data, title }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!data) return null;

  return (
    <div className="bg-gray-100 border border-gray-300 rounded-lg p-4 mb-4">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full text-left font-medium text-gray-700 hover:text-gray-900"
      >
        <span>{title}</span>
        <span className="text-sm">
          {isExpanded ? '收起' : '展开'} 调试信息
        </span>
      </button>
      
      {isExpanded && (
        <div className="mt-4">
          <pre className="bg-white p-3 rounded border text-xs overflow-auto max-h-96">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default DebugInfo;
