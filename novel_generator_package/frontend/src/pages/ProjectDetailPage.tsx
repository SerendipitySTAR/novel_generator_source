import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsApi, conceptsApi, worldSettingsApi, plotOutlinesApi, charactersApi, chaptersApi } from '../api';
import { toast } from 'react-hot-toast';

const ProjectDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<any>(null);
  const [concepts, setConcepts] = useState<any[]>([]);
  const [worldSettings, setWorldSettings] = useState<any[]>([]);
  const [plotOutlines, setPlotOutlines] = useState<any[]>([]);
  const [characters, setCharacters] = useState<any[]>([]);
  const [chapters, setChapters] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editedTitle, setEditedTitle] = useState<string>('');
  const [editedDescription, setEditedDescription] = useState<string>('');

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  const fetchProjectData = async () => {
    try {
      setLoading(true);

      // 获取项目信息
      try {
        const projectData = await projectsApi.getProject(projectId!);
        setProject(projectData);
        setEditedTitle(projectData.title || '');
        setEditedDescription(projectData.description || '');
      } catch (error) {
        console.error('获取项目信息失败:', error);
        // 不显示错误提示，继续获取其他数据
      }

      // 获取概述
      try {
        const conceptsData = await conceptsApi.getConcepts(projectId!);
        setConcepts(conceptsData || []);
      } catch (error) {
        console.error('获取概述失败:', error);
        setConcepts([]);
      }

      // 获取世界观设定
      try {
        const worldSettingsData = await worldSettingsApi.getWorldSettings(projectId!);
        setWorldSettings(worldSettingsData || []);
      } catch (error) {
        console.error('获取世界观设定失败:', error);
        setWorldSettings([]);
      }

      // 获取大纲
      try {
        const plotOutlinesData = await plotOutlinesApi.getPlotOutlines(projectId!);
        setPlotOutlines(plotOutlinesData || []);
      } catch (error) {
        console.error('获取大纲失败:', error);
        setPlotOutlines([]);
      }

      // 获取人物设定
      try {
        const charactersData = await charactersApi.getCharacters(projectId!);
        setCharacters(charactersData || []);
      } catch (error) {
        console.error('获取人物设定失败:', error);
        setCharacters([]);
      }

      // 获取章节
      try {
        const chaptersData = await chaptersApi.getChapters(projectId!);
        setChapters(chaptersData || []);
      } catch (error) {
        console.error('获取章节失败:', error);
        setChapters([]);
      }

      setLoading(false);
    } catch (error) {
      console.error('获取项目数据失败:', error);
      setLoading(false);
    }
  };

  const handleSaveProject = async () => {
    try {
      const updatedProject = await projectsApi.updateProject(projectId!, {
        title: editedTitle,
        description: editedDescription
      });
      
      setProject(updatedProject);
      setEditMode(false);
      toast.success('项目更新成功');
    } catch (error) {
      console.error('更新项目失败:', error);
      toast.error('更新项目失败');
    }
  };

  const handleDeleteProject = async () => {
    if (!window.confirm('确定要删除这个项目吗？此操作不可撤销。')) {
      return;
    }

    try {
      await projectsApi.deleteProject(projectId!);
      toast.success('项目已删除');
      navigate('/projects');
    } catch (error) {
      console.error('删除项目失败:', error);
      toast.error('删除项目失败');
    }
  };

  const getProgressPercentage = () => {
    const totalSteps = 5; // 固定5个步骤：概述、世界观、大纲、人物、章节
    let completed = 0;

    // 检查概述是否完成
    if (concepts.length > 0 && concepts.some(concept => concept.is_selected)) {
      completed++;
    }

    // 检查世界观设定是否完成
    if (worldSettings.length > 0 && worldSettings.some(setting => setting.is_selected)) {
      completed++;
    }

    // 检查大纲是否完成
    if (plotOutlines.length > 0 && plotOutlines.some(outline => outline.is_selected)) {
      completed++;
    }

    // 检查人物设定是否完成
    if (characters.length > 0 && characters.some(character => character.is_selected)) {
      completed++;
    }

    // 检查章节是否完成
    if (chapters.length > 0) {
      completed++;
    }

    return Math.round((completed / totalSteps) * 100);
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        {editMode ? (
          <div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
                项目标题
              </label>
              <input
                id="title"
                type="text"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
              />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
                项目描述
              </label>
              <textarea
                id="description"
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                rows={3}
                value={editedDescription}
                onChange={(e) => setEditedDescription(e.target.value)}
              />
            </div>
            <div className="flex justify-end space-x-2">
              <button
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
                onClick={() => {
                  setEditMode(false);
                  setEditedTitle(project.title || '');
                  setEditedDescription(project.description || '');
                }}
              >
                取消
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                onClick={handleSaveProject}
              >
                保存
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-2xl font-bold">{project?.title || '未命名项目'}</h1>
              <div className="flex space-x-2">
                <button
                  className="px-3 py-1 border border-gray-300 rounded text-gray-700 hover:bg-gray-100 transition-colors"
                  onClick={() => setEditMode(true)}
                >
                  编辑
                </button>
                <button
                  className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                  onClick={handleDeleteProject}
                >
                  删除
                </button>
              </div>
            </div>
            <p className="text-gray-600 mb-4">{project?.description}</p>
            <div className="flex justify-between items-center text-sm text-gray-500">
              <p>创建于: {new Date(project?.created_at).toLocaleString()}</p>
              <p>最后更新: {new Date(project?.updated_at).toLocaleString()}</p>
            </div>
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">项目进度</h2>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div
            className="bg-blue-600 h-4 rounded-full"
            style={{ width: `${getProgressPercentage()}%` }}
          ></div>
        </div>
        <p className="text-gray-600">完成度: {getProgressPercentage()}%</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">创作流程</h2>
          <ul className="space-y-4">
            <li className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${concepts.length > 0 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                1
              </div>
              <div>
                <p className="font-medium">小说概述</p>
                <p className="text-sm text-gray-600">
                  {concepts.length > 0 
                    ? `已生成 ${concepts.length} 个概述` 
                    : '尚未生成概述'}
                </p>
              </div>
              <button
                className="ml-auto px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                onClick={() => navigate(`/projects/${projectId}/concepts`)}
              >
                {concepts.length > 0 ? '查看' : '开始'}
              </button>
            </li>
            
            <li className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${worldSettings.length > 0 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                2
              </div>
              <div>
                <p className="font-medium">世界观设定</p>
                <p className="text-sm text-gray-600">
                  {worldSettings.length > 0 
                    ? `已生成 ${worldSettings.length} 个世界观设定` 
                    : '尚未生成世界观设定'}
                </p>
              </div>
              <button
                className="ml-auto px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                onClick={() => navigate(`/projects/${projectId}/world-settings`)}
              >
                {worldSettings.length > 0 ? '查看' : '开始'}
              </button>
            </li>
            
            <li className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${plotOutlines.length > 0 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                3
              </div>
              <div>
                <p className="font-medium">章节大纲</p>
                <p className="text-sm text-gray-600">
                  {plotOutlines.length > 0 
                    ? `已生成 ${plotOutlines.length} 个大纲` 
                    : '尚未生成大纲'}
                </p>
              </div>
              <button
                className="ml-auto px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                onClick={() => navigate(`/projects/${projectId}/plot-outlines`)}
              >
                {plotOutlines.length > 0 ? '查看' : '开始'}
              </button>
            </li>
            
            <li className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${characters.length > 0 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                4
              </div>
              <div>
                <p className="font-medium">人物设定</p>
                <p className="text-sm text-gray-600">
                  {characters.length > 0 
                    ? `已生成 ${characters.length} 套人物设定` 
                    : '尚未生成人物设定'}
                </p>
              </div>
              <button
                className="ml-auto px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                onClick={() => navigate(`/projects/${projectId}/characters`)}
              >
                {characters.length > 0 ? '查看' : '开始'}
              </button>
            </li>
            
            <li className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${chapters.length > 0 ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                5
              </div>
              <div>
                <p className="font-medium">章节内容</p>
                <p className="text-sm text-gray-600">
                  {chapters.length > 0 
                    ? `已生成 ${chapters.length} 个章节` 
                    : '尚未生成章节内容'}
                </p>
              </div>
              <button
                className="ml-auto px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                onClick={() => navigate(`/projects/${projectId}/chapters`)}
              >
                {chapters.length > 0 ? '查看' : '开始'}
              </button>
            </li>
          </ul>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">最近章节</h2>
          {chapters.length > 0 ? (
            <div className="space-y-4">
              {chapters.slice(0, 3).map((chapter) => (
                <div 
                  key={chapter.id} 
                  className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => navigate(`/projects/${projectId}/chapters/${chapter.id}`)}
                >
                  <h3 className="font-medium mb-2">第{chapter.chapter_number}章: {chapter.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {chapter.content.substring(0, 100)}...
                  </p>
                </div>
              ))}
              {chapters.length > 3 && (
                <div className="text-center mt-4">
                  <button
                    className="text-blue-600 hover:text-blue-800"
                    onClick={() => navigate(`/projects/${projectId}/chapters`)}
                  >
                    查看全部章节
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">尚未生成任何章节</p>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                onClick={() => navigate(`/projects/${projectId}/chapters`)}
              >
                开始生成章节
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectDetailPage;
