import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsApi, chaptersApi, plotOutlinesApi, charactersApi, worldSettingsApi } from '../api';
import { toast } from 'react-hot-toast';

const ChaptersPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<any>(null);
  const [selectedPlotOutline, setSelectedPlotOutline] = useState<any>(null);
  const [selectedCharacter, setSelectedCharacter] = useState<any>(null);
  const [selectedWorldSetting, setSelectedWorldSetting] = useState<any>(null);
  const [chapters, setChapters] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [currentChapterIndex, setCurrentChapterIndex] = useState<number>(0);
  const [writingStyle, setWritingStyle] = useState<string>('详细生动');

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  const fetchProjectData = async () => {
    try {
      setLoading(true);
      
      // 获取项目信息
      const projectData = await projectsApi.getProject(projectId!);
      setProject(projectData);
      
      // 获取已选择的大纲
      const plotOutlinesData = await plotOutlinesApi.getPlotOutlines(projectId!);
      const selectedOutlineData = plotOutlinesData.find((outline: any) => outline.is_selected);
      
      if (!selectedOutlineData) {
        toast.error('请先选择一个大纲');
        navigate(`/projects/${projectId}/plot-outlines`);
        return;
      }
      
      setSelectedPlotOutline(selectedOutlineData);
      
      // 获取已选择的人物设定
      const charactersData = await charactersApi.getCharacters(projectId!);
      const selectedCharacterData = charactersData.find((character: any) => character.is_selected);
      
      if (!selectedCharacterData) {
        toast.error('请先选择人物设定');
        navigate(`/projects/${projectId}/characters`);
        return;
      }
      
      setSelectedCharacter(selectedCharacterData);
      
      // 获取已选择的世界观设定
      const worldSettingsData = await worldSettingsApi.getWorldSettings(projectId!);
      const selectedSettingData = worldSettingsData.find((setting: any) => setting.is_selected);
      
      if (!selectedSettingData) {
        toast.error('请先选择一个世界观设定');
        navigate(`/projects/${projectId}/world-settings`);
        return;
      }
      
      setSelectedWorldSetting(selectedSettingData);
      
      // 获取章节
      const chaptersData = await chaptersApi.getChapters(projectId!);
      setChapters(chaptersData);

      // 设置当前章节索引为已生成章节数量
      setCurrentChapterIndex(chaptersData.length);

      setLoading(false);
    } catch (error) {
      console.error('获取数据失败:', error);
      toast.error('获取项目数据失败');
      setLoading(false);
    }
  };

  const handleGenerateChapter = async () => {
    if (!selectedPlotOutline || !selectedCharacter || !selectedWorldSetting) {
      toast.error('请先完成前面的步骤');
      return;
    }

    try {
      setGenerating(true);
      
      // 获取当前要生成的章节大纲
      const chapterOutlines = selectedPlotOutline.content.chapter_details;
      if (!chapterOutlines || currentChapterIndex >= chapterOutlines.length) {
        toast.error('无法获取章节大纲');
        setGenerating(false);
        return;
      }
      
      const chapterOutline = chapterOutlines[currentChapterIndex];
      
      // 获取前情提要（如果有前一章）
      let previousSummary = "";
      if (chapters.length > 0) {
        // 获取最后一章作为前情提要
        const lastChapter = chapters[chapters.length - 1];
        if (lastChapter) {
          // 简单截取前一章内容的前200个字符作为摘要
          previousSummary = lastChapter.content.substring(0, 200) + "...";
        }
      }
      
      const result = await chaptersApi.generateChapter(projectId!, {
        chapter_outline: chapterOutline,
        world_setting: selectedWorldSetting.content,
        character_profiles: [selectedCharacter.content],
        previous_summary: previousSummary,
        kb_context: [],
        writing_style: writingStyle
      });
      
      // 更新章节列表
      const newChapters = [...chapters, result];
      setChapters(newChapters);

      // 更新当前章节索引
      setCurrentChapterIndex(newChapters.length);
      
      toast.success('章节生成成功');
      setGenerating(false);
    } catch (error) {
      console.error('生成章节失败:', error);
      let errorMessage = '生成章节失败';
      if (error instanceof Error) {
        errorMessage = `生成章节失败: ${error.message}`;
      }
      toast.error(errorMessage);
      setGenerating(false);
    }
  };

  const handleViewChapter = (chapterId: string) => {
    navigate(`/projects/${projectId}/chapters/${chapterId}`);
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
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">{project?.title || '未命名项目'}</h1>
        <p className="text-gray-600">{project?.description}</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">章节生成</h2>
        <p className="text-gray-600 mb-4">
          基于您选择的大纲、人物设定和世界观，AI将为您生成小说章节内容
        </p>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="writingStyle">
            写作风格
          </label>
          <select
            id="writingStyle"
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={writingStyle}
            onChange={(e) => setWritingStyle(e.target.value)}
          >
            <option value="详细生动">详细生动</option>
            <option value="简洁明快">简洁明快</option>
            <option value="诗意唯美">诗意唯美</option>
            <option value="悬疑紧张">悬疑紧张</option>
            <option value="幽默风趣">幽默风趣</option>
          </select>
        </div>
        
        <div className="mb-6">
          <h3 className="font-semibold mb-2">当前进度:</h3>
          <p className="text-gray-700">
            已生成 {chapters.length} 章 / 大纲共 {selectedPlotOutline?.content?.chapter_details?.length || 0} 章
          </p>

          {/* 前置条件检查 */}
          <div className="mt-4 space-y-2">
            <div className={`flex items-center ${selectedPlotOutline ? 'text-green-600' : 'text-red-600'}`}>
              <span className="mr-2">{selectedPlotOutline ? '✅' : '❌'}</span>
              <span>大纲已选择</span>
            </div>
            <div className={`flex items-center ${selectedCharacter ? 'text-green-600' : 'text-red-600'}`}>
              <span className="mr-2">{selectedCharacter ? '✅' : '❌'}</span>
              <span>人物设定已选择</span>
            </div>
            <div className={`flex items-center ${selectedWorldSetting ? 'text-green-600' : 'text-red-600'}`}>
              <span className="mr-2">{selectedWorldSetting ? '✅' : '❌'}</span>
              <span>世界观设定已选择</span>
            </div>
          </div>
          
          {selectedPlotOutline?.content?.chapter_details && currentChapterIndex < selectedPlotOutline.content.chapter_details.length && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">下一章大纲:</h4>
              <p className="text-gray-700">
                第{selectedPlotOutline.content.chapter_details[currentChapterIndex].number}章: {selectedPlotOutline.content.chapter_details[currentChapterIndex].title}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                主要场景: {selectedPlotOutline.content.chapter_details[currentChapterIndex].scenes}
              </p>
            </div>
          )}
        </div>
        
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          onClick={handleGenerateChapter}
          disabled={generating || !selectedPlotOutline || !selectedCharacter || !selectedWorldSetting || (selectedPlotOutline?.content?.chapter_details && currentChapterIndex >= selectedPlotOutline.content.chapter_details.length)}
        >
          {generating ? '生成中...' : currentChapterIndex < (selectedPlotOutline?.content?.chapter_details?.length || 0) ? '生成下一章' : '所有章节已生成'}
        </button>
      </div>

      {chapters.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">已生成章节</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {chapters.map((chapter) => (
              <div 
                key={chapter.id} 
                className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleViewChapter(chapter.id)}
              >
                <h3 className="font-medium mb-2">第{chapter.chapter_number}章: {chapter.title}</h3>
                <p className="text-sm text-gray-600 line-clamp-3">
                  {chapter.content.substring(0, 100)}...
                </p>
                <div className="flex justify-between items-center mt-4">
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                    {chapter.status === 'draft' ? '草稿' : '已完成'}
                  </span>
                  <button
                    className="text-blue-600 hover:text-blue-800"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewChapter(chapter.id);
                    }}
                  >
                    查看全文
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChaptersPage;
