import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsApi } from '../api';
import { PlusCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

const ProjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [newProjectTitle, setNewProjectTitle] = useState<string>('');
  const [newProjectDescription, setNewProjectDescription] = useState<string>('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await projectsApi.getProjects();
      setProjects(data);
      setLoading(false);
    } catch (error) {
      console.error('获取项目失败:', error);
      toast.error('获取项目列表失败');
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    if (!newProjectTitle.trim()) {
      toast.error('请输入项目标题');
      return;
    }

    try {
      const newProject = await projectsApi.createProject({
        title: newProjectTitle,
        description: newProjectDescription,
      });
      
      setProjects([...projects, newProject]);
      setShowCreateModal(false);
      setNewProjectTitle('');
      setNewProjectDescription('');
      toast.success('项目创建成功');
      
      // 导航到新项目的概述页面
      navigate(`/projects/${newProject.id}/concepts`);
    } catch (error) {
      console.error('创建项目失败:', error);
      toast.error('创建项目失败');
    }
  };

  const handleDeleteProject = async (projectId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('确定要删除这个项目吗？此操作不可撤销。')) {
      return;
    }

    try {
      await projectsApi.deleteProject(projectId);
      setProjects(projects.filter(project => project.id !== projectId));
      toast.success('项目已删除');
    } catch (error) {
      console.error('删除项目失败:', error);
      toast.error('删除项目失败');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">我的项目</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <PlusCircle className="mr-2 h-5 w-5" />
          创建新项目
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">加载中...</p>
        </div>
      ) : projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.id}
              className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <h3 className="text-xl font-semibold mb-2">{project.title || '未命名项目'}</h3>
              {project.description && (
                <p className="text-gray-600 mb-4 line-clamp-2">{project.description}</p>
              )}
              <div className="flex justify-between items-center mt-4">
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                  {project.status === 'draft' ? '草稿' : '已完成'}
                </span>
                <div className="flex space-x-2">
                  <button
                    className="text-blue-600 hover:text-blue-800"
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/projects/${project.id}`);
                    }}
                  >
                    查看
                  </button>
                  <button
                    className="text-red-600 hover:text-red-800"
                    onClick={(e) => handleDeleteProject(project.id, e)}
                  >
                    删除
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-4">
                创建于: {new Date(project.created_at).toLocaleString()}
              </p>
              <p className="text-xs text-gray-500">
                最后更新: {new Date(project.updated_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <h3 className="text-xl font-semibold mb-4">还没有项目</h3>
          <p className="text-gray-600 mb-6">创建您的第一个小说项目，开始AI辅助创作之旅</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            创建新项目
          </button>
        </div>
      )}

      {/* 创建项目模态框 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">创建新项目</h2>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
                项目标题 *
              </label>
              <input
                id="title"
                type="text"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                placeholder="输入项目标题"
                value={newProjectTitle}
                onChange={(e) => setNewProjectTitle(e.target.value)}
              />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
                项目描述 (可选)
              </label>
              <textarea
                id="description"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                placeholder="输入项目描述"
                rows={3}
                value={newProjectDescription}
                onChange={(e) => setNewProjectDescription(e.target.value)}
              />
            </div>
            <div className="flex justify-end space-x-2">
              <button
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                onClick={() => setShowCreateModal(false)}
              >
                取消
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                onClick={handleCreateProject}
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectsPage;
