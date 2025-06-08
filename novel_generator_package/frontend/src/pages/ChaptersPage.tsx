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
  const [useQualityCheck, setUseQualityCheck] = useState<boolean>(true);

  useEffect(() => {
    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  // 添加强制刷新章节的函数
  const forceRefreshChapters = async () => {
    try {
      console.log('强制刷新章节列表，项目ID:', projectId);

      // 添加重试机制
      let retryCount = 0;
      const maxRetries = 3;
      let updatedChapters;

      while (retryCount < maxRetries) {
        try {
          updatedChapters = await chaptersApi.getChapters(projectId!);
          break; // 成功获取，跳出重试循环
        } catch (error) {
          retryCount++;
          console.warn(`第${retryCount}次获取章节列表失败:`, error);

          if (retryCount < maxRetries) {
            // 等待一段时间后重试
            await new Promise(resolve => setTimeout(resolve, 1000 * retryCount));
          } else {
            throw error; // 达到最大重试次数，抛出错误
          }
        }
      }

      console.log('刷新后的章节列表:', updatedChapters);

      // 按章节号排序
      const sortedChapters = updatedChapters.sort((a, b) => a.chapter_number - b.chapter_number);

      setChapters(sortedChapters);
      setCurrentChapterIndex(sortedChapters.length);
      setGenerating(false);

      return sortedChapters;
    } catch (error) {
      console.error('刷新章节失败:', error);
      throw error;
    }
  };

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
      console.log('初始加载的章节数据:', chaptersData);

      // 按章节号排序
      const sortedChapters = chaptersData.sort((a, b) => a.chapter_number - b.chapter_number);
      setChapters(sortedChapters);

      // 设置当前章节索引为已生成章节数量
      setCurrentChapterIndex(sortedChapters.length);

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

    // 验证项目ID
    if (!projectId) {
      toast.error('项目ID无效');
      return;
    }

    try {
      setGenerating(true);

      console.log('开始生成章节，项目ID:', projectId);
      console.log('选中的大纲:', selectedPlotOutline);
      console.log('选中的人物:', selectedCharacter);
      console.log('选中的世界观:', selectedWorldSetting);
      
      // 获取当前要生成的章节大纲
      const chapterOutlines = selectedPlotOutline.content.chapter_details;
      if (!chapterOutlines || currentChapterIndex >= chapterOutlines.length) {
        toast.error('无法获取章节大纲');
        setGenerating(false);
        return;
      }

      const chapterOutline = chapterOutlines[currentChapterIndex];
      console.log('当前章节索引:', currentChapterIndex);
      console.log('选择的章节大纲:', chapterOutline);
      console.log('所有章节大纲:', chapterOutlines);
      
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
      
      let result;

      if (useQualityCheck) {
        // 使用带质量检查的API
        result = await chaptersApi.generateChapterWithQualityCheck(projectId!, {
          chapter_outline: chapterOutline,
          world_setting: selectedWorldSetting.content,
          character_profiles: [selectedCharacter.content],
          previous_summary: previousSummary,
          previous_chapters: chapters,
          kb_context: [],
          writing_style: writingStyle,
          max_retries: 2
        });
      } else {
        // 使用普通API
        result = await chaptersApi.generateChapter(projectId!, {
          chapter_outline: chapterOutline,
          world_setting: selectedWorldSetting.content,
          character_profiles: [selectedCharacter.content],
          previous_summary: previousSummary,
          kb_context: [],
          writing_style: writingStyle
        });
      }

      console.log('章节生成成功，返回结果:', result);

      // 自动刷新章节列表
      console.log('开始自动刷新章节列表...');
      try {
        // 等待一小段时间确保数据库写入完成
        await new Promise(resolve => setTimeout(resolve, 500));

        const updatedChaptersData = await forceRefreshChapters();
        console.log('自动刷新后的章节列表:', updatedChaptersData);

        // 显示成功消息
        toast.success(`✅ 章节生成成功！已生成第${result.chapter_number || currentChapterIndex + 1}章: ${result.title || '新章节'}，章节列表已自动更新`);

        // 确保UI状态正确更新
        setGenerating(false);

      } catch (refreshError) {
        console.error('自动刷新章节列表失败:', refreshError);

        // 如果自动刷新失败，尝试手动添加新章节到列表
        try {
          const newChapter = {
            id: result.id,
            chapter_number: result.chapter_number,
            title: result.title,
            content: result.content,
            word_count: result.word_count,
            writing_style: result.writing_style,
            status: result.status,
            created_at: result.created_at,
            updated_at: result.updated_at
          };

          // 添加新章节到现有列表
          const updatedChapters = [...chapters, newChapter].sort((a, b) => a.chapter_number - b.chapter_number);
          setChapters(updatedChapters);
          setCurrentChapterIndex(updatedChapters.length);

          toast.success(`✅ 章节生成成功！已生成第${result.chapter_number || currentChapterIndex + 1}章: ${result.title || '新章节'}`);
          console.log('使用备用方案更新章节列表成功');

        } catch (fallbackError) {
          console.error('备用方案也失败了:', fallbackError);
          toast.success(`✅ 章节生成成功！请点击"刷新章节"按钮查看新章节`);
        }

        setGenerating(false);
      }
    } catch (error) {
      console.error('生成章节失败:', error);
      console.error('错误详情:', {
        error,
        projectId,
        useQualityCheck,
        chapterOutline: selectedPlotOutline?.content?.chapter_details?.[currentChapterIndex]
      });

      let errorMessage = '生成章节失败';

      if (error instanceof Error) {
        errorMessage = `生成章节失败: ${error.message}`;

        // 特殊处理 Method Not Allowed 错误
        if (error.message.includes('Method Not Allowed')) {
          errorMessage = '生成章节失败: 服务器路由错误，请刷新页面后重试';
          console.error('检测到 Method Not Allowed 错误，可能的原因：');
          console.error('1. 浏览器缓存问题');
          console.error('2. 网络连接问题');
          console.error('3. 服务器重启导致的临时问题');
        }

        // 添加更多错误类型的处理
        if (error.message.includes('项目不存在')) {
          errorMessage = '生成章节失败: 项目不存在，请检查项目ID';
        } else if (error.message.includes('404')) {
          errorMessage = '生成章节失败: 资源不存在，请检查项目配置';
        } else if (error.message.includes('500')) {
          errorMessage = '生成章节失败: 服务器内部错误，请稍后重试';
        }
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
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="writingStyle">
              写作风格
            </label>
            <select
              id="writingStyle"
              className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline w-full"
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

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              生成选项
            </label>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="useQualityCheck"
                className="mr-2"
                checked={useQualityCheck}
                onChange={(e) => setUseQualityCheck(e.target.checked)}
              />
              <label htmlFor="useQualityCheck" className="text-gray-700 text-sm">
                启用质量检查和智能重试
              </label>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              启用后将自动检查内容质量和连贯性，必要时重新生成
            </p>
          </div>
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
        
        <div className="flex space-x-4">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            onClick={handleGenerateChapter}
            disabled={generating || !selectedPlotOutline || !selectedCharacter || !selectedWorldSetting}
          >
            {generating ? '生成中...' :
             currentChapterIndex < (selectedPlotOutline?.content?.chapter_details?.length || 0) ?
             `生成第${currentChapterIndex + 1}章` :
             '重新生成最后一章'}
          </button>

          <button
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
            onClick={async () => {
              try {
                setLoading(true);
                const updatedChapters = await forceRefreshChapters();
                toast.success(`✅ 刷新完成，当前有 ${updatedChapters.length} 个章节`);
              } catch (error) {
                console.error('手动刷新失败:', error);
                toast.error('❌ 刷新失败，请稍后重试');
              } finally {
                setLoading(false);
              }
            }}
            disabled={loading || generating}
          >
            {loading ? '刷新中...' : '刷新章节'}
          </button>

          {currentChapterIndex >= (selectedPlotOutline?.content?.chapter_details?.length || 0) && (
            <div className="flex items-center text-green-600">
              <span className="mr-2">✅</span>
              <span>所有章节已生成完成</span>
            </div>
          )}
        </div>
      </div>

      {chapters.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">已生成章节 (共{chapters.length}章)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {chapters.map((chapter) => (
              <div 
                key={chapter.id} 
                className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleViewChapter(chapter.id)}
              >
                <h3 className="font-medium mb-2">第{chapter.chapter_number}章: {chapter.title}</h3>
                <p className="text-sm text-gray-600 line-clamp-3">
                  {chapter.content ? chapter.content.substring(0, 100) + '...' : '内容加载中...'}
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

      {/* 调试信息 */}
      <div className="mb-8 p-4 bg-gray-100 rounded-lg">
        <h3 className="font-semibold mb-2">调试信息:</h3>
        <p>章节数量: {chapters.length}</p>
        <p>当前章节索引: {currentChapterIndex}</p>
        <p>项目ID: {projectId}</p>
        <p>生成状态: {generating ? '正在生成' : '未生成'}</p>
        <p>使用质量检查: {useQualityCheck ? '是' : '否'}</p>
        <p>章节数据: {JSON.stringify(chapters.map(c => ({id: c.id, title: c.title, chapter_number: c.chapter_number, content_length: c.content?.length || 0})), null, 2)}</p>
        <p>章节列表显示条件: {chapters.length > 0 ? '满足' : '不满足'}</p>

        {/* 手动测试按钮 */}
        <div className="mt-4 space-x-2">
          <button
            className="px-3 py-1 bg-green-600 text-white rounded text-sm"
            onClick={async () => {
              try {
                console.log('手动测试：获取章节列表');
                const result = await chaptersApi.getChapters(projectId!);
                console.log('手动测试结果:', result);
                alert(`获取到 ${result.length} 个章节`);
              } catch (error) {
                console.error('手动测试失败:', error);
                alert(`测试失败: ${error}`);
              }
            }}
          >
            测试获取章节
          </button>

          <button
            className="px-3 py-1 bg-blue-600 text-white rounded text-sm"
            onClick={() => {
              console.log('当前状态:', {
                projectId,
                chapters,
                selectedPlotOutline,
                selectedCharacter,
                selectedWorldSetting
              });
            }}
          >
            打印状态
          </button>

          <button
            className="px-3 py-1 bg-yellow-600 text-white rounded text-sm"
            onClick={async () => {
              try {
                console.log('强制刷新章节列表');
                const updatedChapters = await chaptersApi.getChapters(projectId!);
                console.log('刷新后的章节列表:', updatedChapters);
                setChapters(updatedChapters);
                setCurrentChapterIndex(updatedChapters.length);
                setGenerating(false); // 确保重置生成状态
                alert(`刷新完成，当前有 ${updatedChapters.length} 个章节`);
              } catch (error) {
                console.error('刷新失败:', error);
                alert(`刷新失败: ${error}`);
              }
            }}
          >
            强制刷新
          </button>

          <button
            className="px-3 py-1 bg-red-600 text-white rounded text-sm"
            onClick={async () => {
              if (!selectedPlotOutline || !selectedCharacter || !selectedWorldSetting) {
                alert('前置条件不满足');
                return;
              }

              try {
                console.log('手动测试：章节生成API');
                const chapterOutline = selectedPlotOutline.content.chapter_details[0];
                console.log('使用的章节大纲:', chapterOutline);

                const testData = {
                  chapter_outline: chapterOutline,
                  world_setting: selectedWorldSetting.content,
                  character_profiles: [selectedCharacter.content],
                  previous_summary: "",
                  kb_context: [],
                  writing_style: "详细生动"
                };

                console.log('发送的测试数据:', testData);

                const result = await chaptersApi.generateChapter(projectId!, testData);
                console.log('章节生成测试结果:', result);
                alert(`测试成功！生成了章节: ${result.title}`);

                // 重新获取章节列表
                const updatedChapters = await chaptersApi.getChapters(projectId!);
                setChapters(updatedChapters);
                setCurrentChapterIndex(updatedChapters.length);

              } catch (error) {
                console.error('章节生成测试失败:', error);
                alert(`测试失败: ${error}`);
              }
            }}
          >
            测试生成章节
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChaptersPage;
