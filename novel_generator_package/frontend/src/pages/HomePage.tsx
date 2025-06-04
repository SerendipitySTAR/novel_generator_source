import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsApi } from '../api';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [recentProjects, setRecentProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const projects = await projectsApi.getProjects();
        // 获取最近的3个项目
        setRecentProjects(projects.slice(0, 3));
        setLoading(false);
      } catch (error) {
        console.error('获取项目失败:', error);
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const handleCreateProject = () => {
    navigate('/projects');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">欢迎使用自动小说生成器</h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          基于多智能体协作的全自动多轮交互式小说生成器，让AI助力您的创作之旅
        </p>
        <button
          onClick={handleCreateProject}
          className="mt-6 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          开始创作
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">智能创意生成</h3>
          <p className="text-gray-600">
            基于您的简单输入，AI智能体将生成多个引人入胜的小说创意概述，让您选择最喜欢的方向
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">完整世界观构建</h3>
          <p className="text-gray-600">
            自动构建丰富、自洽的世界观设定，包括地理环境、历史背景、势力组织、能量体系等
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="h-12 w-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">多轮交互式创作</h3>
          <p className="text-gray-600">
            在创作过程中随时调整方向，选择剧情分支，让您的小说创作更加灵活多变
          </p>
        </div>
      </div>

      <div className="bg-gray-50 p-8 rounded-lg">
        <h2 className="text-2xl font-bold mb-6">最近的项目</h2>
        {loading ? (
          <p className="text-gray-500">加载中...</p>
        ) : recentProjects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentProjects.map((project) => (
              <div
                key={project.id}
                className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <h3 className="text-lg font-semibold mb-2">{project.title || '未命名项目'}</h3>
                <p className="text-sm text-gray-500 mb-4">
                  最后更新: {new Date(project.updated_at).toLocaleString()}
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                    {project.status === 'draft' ? '草稿' : '已完成'}
                  </span>
                  <button
                    className="text-blue-600 hover:text-blue-800"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/projects/${project.id}`);
                    }}
                  >
                    查看详情
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">您还没有创建任何项目</p>
            <button
              onClick={handleCreateProject}
              className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              创建第一个项目
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;
