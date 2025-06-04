import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsApi, plotOutlinesApi, worldSettingsApi, conceptsApi } from '../api';
import { toast } from 'react-hot-toast';

const PlotOutlinesPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<any>(null);
  const [selectedConcept, setSelectedConcept] = useState<any>(null);
  const [selectedWorldSetting, setSelectedWorldSetting] = useState<any>(null);
  const [plotOutlines, setPlotOutlines] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [chapterCount, setChapterCount] = useState<number>(10);
  const [conflictElements, setConflictElements] = useState<string>('');
  const [showConflictSuggestions, setShowConflictSuggestions] = useState<boolean>(false);
  const [editingOutlineId, setEditingOutlineId] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState<string>('');

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
      
      // 获取已选择的概述
      const conceptsData = await conceptsApi.getConcepts(projectId!);
      const selectedConceptData = conceptsData.find((concept: any) => concept.is_selected);
      
      if (!selectedConceptData) {
        toast.error('请先选择一个小说概述');
        navigate(`/projects/${projectId}/concepts`);
        return;
      }
      
      setSelectedConcept(selectedConceptData);
      
      // 获取已选择的世界观设定
      const worldSettingsData = await worldSettingsApi.getWorldSettings(projectId!);
      const selectedSettingData = worldSettingsData.find((setting: any) => setting.is_selected);
      
      if (!selectedSettingData) {
        toast.error('请先选择一个世界观设定');
        navigate(`/projects/${projectId}/world-settings`);
        return;
      }
      
      setSelectedWorldSetting(selectedSettingData);
      
      // 获取大纲
      const plotOutlinesData = await plotOutlinesApi.getPlotOutlines(projectId!);
      setPlotOutlines(plotOutlinesData);
      
      setLoading(false);
    } catch (error) {
      console.error('获取数据失败:', error);
      toast.error('获取项目数据失败');
      setLoading(false);
    }
  };

  const handleGeneratePlotOutlines = async () => {
    if (!selectedConcept || !selectedWorldSetting) {
      toast.error('请先选择小说概述和世界观设定');
      return;
    }

    try {
      setGenerating(true);
      
      // 使用选定的概述和世界观设定生成大纲
      const narrativeContent = selectedConcept.expanded_content || selectedConcept.content;
      const conflictElementsList = conflictElements
        .split('\n')
        .map(item => item.trim())
        .filter(item => item.length > 0);
      
      const result = await plotOutlinesApi.generatePlotOutlines(projectId!, {
        chapter_count: chapterCount,
        conflict_elements: conflictElements
      });
      
      // 处理响应数据，确保兼容性
      const plotOutlinesData = result.plot_outlines || result || [];
      setPlotOutlines(plotOutlinesData);
      toast.success('大纲生成成功');
      setGenerating(false);
    } catch (error) {
      console.error('生成大纲失败:', error);
      toast.error('生成大纲失败');
      setGenerating(false);
    }
  };

  const handleSelectPlotOutline = async (outlineId: string) => {
    try {
      await plotOutlinesApi.selectPlotOutline(projectId!, outlineId);

      // 更新本地状态
      setPlotOutlines(plotOutlines.map(outline => ({
        ...outline,
        is_selected: outline.id === outlineId
      })));

      toast.success('已选择大纲');
    } catch (error) {
      console.error('选择大纲失败:', error);
      toast.error('选择大纲失败');
    }
  };

  const handleAddConflictSuggestion = (suggestion: string) => {
    const currentElements = conflictElements.split('\n').filter(item => item.trim().length > 0);
    if (!currentElements.includes(suggestion)) {
      const newElements = [...currentElements, suggestion].join('\n');
      setConflictElements(newElements);
    }
  };

  const getConflictSuggestions = () => {
    // 根据世界观设定生成建议的冲突元素
    const suggestions = [
      '主角与反派的对抗',
      '家族内部的权力斗争',
      '爱情与责任的抉择',
      '正义与利益的冲突',
      '传统与现代的碰撞',
      '个人理想与现实的矛盾',
      '友情与背叛的考验',
      '生存与道德的选择',
      '过去秘密的揭露',
      '身份认同的危机',
      '资源争夺的竞争',
      '信仰与怀疑的斗争'
    ];

    return suggestions;
  };

  const handleEditOutline = (outline: any) => {
    setEditingOutlineId(outline.id);
    // 将内容转换为可编辑的字符串格式
    const contentStr = typeof outline.content === 'string'
      ? outline.content
      : JSON.stringify(outline.content, null, 2);
    setEditedContent(contentStr);
  };

  const handleSaveEdit = async () => {
    if (!editingOutlineId) return;

    try {
      // 尝试解析为JSON，如果失败则保存为字符串
      let parsedContent;
      try {
        parsedContent = JSON.parse(editedContent);
      } catch {
        parsedContent = editedContent;
      }

      await plotOutlinesApi.updatePlotOutline(projectId!, editingOutlineId, {
        content: parsedContent
      });

      // 更新本地状态
      setPlotOutlines(plotOutlines.map(outline =>
        outline.id === editingOutlineId
          ? { ...outline, content: parsedContent }
          : outline
      ));

      setEditingOutlineId(null);
      setEditedContent('');
      toast.success('大纲编辑成功');
    } catch (error) {
      console.error('编辑大纲失败:', error);
      toast.error('编辑大纲失败');
    }
  };

  const handleCancelEdit = () => {
    setEditingOutlineId(null);
    setEditedContent('');
  };

  const handleContinue = () => {
    const selectedOutline = plotOutlines.find(outline => outline.is_selected);
    if (!selectedOutline) {
      toast.error('请先选择一个大纲');
      return;
    }

    navigate(`/projects/${projectId}/characters`);
  };

  const renderPlotOutlineContent = (outline: any) => {
    const content = outline.content;
    if (!content) return <p className="text-gray-500">暂无内容</p>;

    // 如果content是字符串，直接显示
    if (typeof content === 'string') {
      return (
        <div>
          <h4 className="font-semibold mb-4">大纲内容</h4>
          <div className="whitespace-pre-wrap text-gray-700">{content}</div>
        </div>
      );
    }

    // 如果content是对象，按结构化方式显示
    return (
      <div>
        {content.structure && (
          <>
            <h4 className="font-semibold mb-4">总体故事结构</h4>
            <p className="whitespace-pre-wrap mb-6">{content.structure}</p>
          </>
        )}

        {content.chapters && content.chapters.length > 0 && (
          <>
            <h4 className="font-semibold mb-4">章节列表</h4>
            <div className="mb-6">
              {content.chapters.map((chapter: any, index: number) => (
                <div key={index} className="mb-2">
                  <p>{chapter.number || (index + 1)}. {chapter.title} - {chapter.word_count || '待定'}字</p>
                </div>
              ))}
            </div>
          </>
        )}

        {content.chapter_details && content.chapter_details.length > 0 && (
          <>
            <h4 className="font-semibold mb-4">章节详情</h4>
            <div className="space-y-6">
              {content.chapter_details.map((detail: any, index: number) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium mb-2">第{detail.number || (index + 1)}章: {detail.title}</h5>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {detail.scenes && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">主要场景:</p>
                        <p className="text-gray-600">{detail.scenes}</p>
                      </div>
                    )}
                    {detail.characters && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">出场人物:</p>
                        <p className="text-gray-600">{detail.characters}</p>
                      </div>
                    )}
                    {detail.events && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">核心事件:</p>
                        <p className="text-gray-600">{detail.events}</p>
                      </div>
                    )}
                    {detail.conflicts && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">目标与冲突:</p>
                        <p className="text-gray-600">{detail.conflicts}</p>
                      </div>
                    )}
                    {detail.turning_points && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">关键转折点:</p>
                        <p className="text-gray-600">{detail.turning_points}</p>
                      </div>
                    )}
                    {detail.emotional_tone && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">情感基调:</p>
                        <p className="text-gray-600">{detail.emotional_tone}</p>
                      </div>
                    )}
                    {detail.foreshadowing && (
                      <div className="md:col-span-2">
                        <p className="text-sm font-medium text-gray-700">伏笔/悬念:</p>
                        <p className="text-gray-600">{detail.foreshadowing}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* 如果没有结构化数据，显示原始内容 */}
        {!content.structure && !content.chapters && !content.chapter_details && (
          <div>
            <h4 className="font-semibold mb-4">大纲内容</h4>
            <div className="whitespace-pre-wrap text-gray-700">{JSON.stringify(content, null, 2)}</div>
          </div>
        )}
      </div>
    );
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
        <h2 className="text-xl font-semibold mb-4">大纲生成</h2>
        <p className="text-gray-600 mb-4">
          基于您选择的小说概述和世界观设定，AI将为您生成详细的章节大纲
        </p>
        
        <div className="mb-6">
          <h3 className="font-semibold mb-2">已选择的小说概述:</h3>
          <div className="p-4 bg-gray-50 rounded-lg mb-4">
            <p className="whitespace-pre-wrap line-clamp-3">
              {selectedConcept?.expanded_content || selectedConcept?.content}
            </p>
          </div>
          
          <h3 className="font-semibold mb-2">已选择的世界观设定:</h3>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="whitespace-pre-wrap line-clamp-3">
              {selectedWorldSetting?.content?.description || '世界观设定'}
            </p>
          </div>
        </div>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="chapterCount">
            章节数量
          </label>
          <select
            id="chapterCount"
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={chapterCount}
            onChange={(e) => setChapterCount(parseInt(e.target.value))}
          >
            <option value={5}>5章</option>
            <option value={10}>10章</option>
            <option value={15}>15章</option>
            <option value={20}>20章</option>
            <option value={30}>30章</option>
          </select>
        </div>
        
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <label className="block text-gray-700 text-sm font-bold" htmlFor="conflictElements">
              关键冲突元素 (可选，每行一个)
            </label>
            <button
              type="button"
              className="text-blue-600 hover:text-blue-800 text-sm"
              onClick={() => setShowConflictSuggestions(!showConflictSuggestions)}
            >
              {showConflictSuggestions ? '隐藏建议' : '显示建议'}
            </button>
          </div>

          {showConflictSuggestions && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-3">点击下方建议快速添加冲突元素：</p>
              <div className="flex flex-wrap gap-2">
                {getConflictSuggestions().map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm hover:bg-blue-200 transition-colors"
                    onClick={() => handleAddConflictSuggestion(suggestion)}
                  >
                    + {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <textarea
            id="conflictElements"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="例如：主角与反派的对抗&#10;家族内部的权力斗争&#10;爱情与责任的抉择"
            rows={4}
            value={conflictElements}
            onChange={(e) => setConflictElements(e.target.value)}
          />
        </div>
        
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          onClick={handleGeneratePlotOutlines}
          disabled={generating || !selectedConcept || !selectedWorldSetting}
        >
          {generating ? '生成中...' : '生成大纲'}
        </button>
      </div>

      {plotOutlines.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">小说大纲</h2>
          <p className="text-gray-600 mb-4">
            请选择一个您喜欢的大纲，用于后续的小说创作
          </p>
          
          <div className="space-y-6">
            {plotOutlines.map((outline) => (
              <div 
                key={outline.id} 
                className={`bg-white p-6 rounded-lg shadow-md border-2 ${
                  outline.is_selected ? 'border-blue-500' : 'border-transparent'
                }`}
              >
                {renderPlotOutlineContent(outline)}
                
                <div className="flex justify-between mt-6">
                  <button
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    onClick={() => handleEditOutline(outline)}
                  >
                    编辑大纲
                  </button>
                  <button
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      outline.is_selected
                        ? 'bg-gray-200 text-gray-700'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                    onClick={() => handleSelectPlotOutline(outline.id)}
                    disabled={outline.is_selected}
                  >
                    {outline.is_selected ? '已选择' : '选择此大纲'}
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-8 flex justify-end">
            <button
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              onClick={handleContinue}
            >
              继续下一步
            </button>
          </div>
        </div>
      )}

      {/* 编辑大纲模态框 */}
      {editingOutlineId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">编辑大纲</h3>
            <p className="text-gray-600 mb-4">
              您可以直接编辑大纲内容。支持纯文本或JSON格式。
            </p>

            <textarea
              className="w-full h-96 p-4 border rounded-lg font-mono text-sm"
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              placeholder="请输入大纲内容..."
            />

            <div className="flex justify-end space-x-4 mt-6">
              <button
                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                onClick={handleCancelEdit}
              >
                取消
              </button>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                onClick={handleSaveEdit}
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlotOutlinesPage;
