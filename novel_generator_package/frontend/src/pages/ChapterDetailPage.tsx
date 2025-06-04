import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { chaptersApi } from '../api';
import { toast } from 'react-hot-toast';

const ChapterDetailPage: React.FC = () => {
  const { projectId, chapterId } = useParams<{ projectId: string; chapterId: string }>();
  const navigate = useNavigate();
  
  const [chapter, setChapter] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [polishing, setPolishing] = useState<boolean>(false);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editedContent, setEditedContent] = useState<string>('');
  const [generatingBranches, setGeneratingBranches] = useState<boolean>(false);
  const [plotBranches, setPlotBranches] = useState<any[]>([]);
  const [showBranches, setShowBranches] = useState<boolean>(false);

  useEffect(() => {
    if (projectId && chapterId) {
      fetchChapter();
    }
  }, [projectId, chapterId]);

  const fetchChapter = async () => {
    try {
      setLoading(true);
      const chapterData = await chaptersApi.getChapter(projectId!, chapterId!);
      setChapter(chapterData);
      setEditedContent(chapterData.content);
      setLoading(false);
    } catch (error) {
      console.error('获取章节失败:', error);
      toast.error('获取章节失败');
      setLoading(false);
    }
  };

  const handlePolishChapter = async () => {
    try {
      setPolishing(true);
      const result = await chaptersApi.polishChapter(projectId!, chapterId!, {});
      setChapter(result);
      setEditedContent(result.content);
      toast.success('章节润色成功');
      setPolishing(false);
    } catch (error) {
      console.error('润色章节失败:', error);
      toast.error('润色章节失败');
      setPolishing(false);
    }
  };

  const handleSaveChanges = async () => {
    try {
      const result = await chaptersApi.updateChapter(projectId!, chapterId!, {
        content: editedContent
      });
      setChapter(result);
      setEditMode(false);
      toast.success('章节保存成功');
    } catch (error) {
      console.error('保存章节失败:', error);
      toast.error('保存章节失败');
    }
  };

  const handleGeneratePlotBranches = async () => {
    try {
      setGeneratingBranches(true);
      const result = await chaptersApi.generatePlotBranches(projectId!, chapterId!, {});
      setPlotBranches(result.plot_branches || []);
      setShowBranches(true);
      toast.success('剧情分支生成成功');
      setGeneratingBranches(false);
    } catch (error) {
      console.error('生成剧情分支失败:', error);
      toast.error('生成剧情分支失败');
      setGeneratingBranches(false);
    }
  };

  const handleBackToChapters = () => {
    navigate(`/projects/${projectId}/chapters`);
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
      <div className="mb-6">
        <button
          className="flex items-center text-blue-600 hover:text-blue-800"
          onClick={handleBackToChapters}
        >
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回章节列表
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">第{chapter.chapter_number}章: {chapter.title}</h1>
          <div className="flex space-x-2">
            {!editMode ? (
              <>
                <button
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  onClick={() => setEditMode(true)}
                >
                  编辑
                </button>
                <button
                  className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors disabled:bg-gray-400"
                  onClick={handlePolishChapter}
                  disabled={polishing}
                >
                  {polishing ? '润色中...' : '润色'}
                </button>
                <button
                  className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 transition-colors disabled:bg-gray-400"
                  onClick={handleGeneratePlotBranches}
                  disabled={generatingBranches}
                >
                  {generatingBranches ? '生成中...' : '生成剧情分支'}
                </button>
              </>
            ) : (
              <>
                <button
                  className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                  onClick={() => {
                    setEditMode(false);
                    setEditedContent(chapter.content);
                  }}
                >
                  取消
                </button>
                <button
                  className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  onClick={handleSaveChanges}
                >
                  保存
                </button>
              </>
            )}
          </div>
        </div>

        <div className="mb-4">
          <p className="text-sm text-gray-500">
            最后更新: {new Date(chapter.updated_at).toLocaleString()}
          </p>
        </div>

        {editMode ? (
          <textarea
            className="w-full h-96 p-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
          />
        ) : (
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {chapter.content || '暂无章节内容'}
            </div>
            {!chapter.content && (
              <div className="text-center py-8 text-gray-500">
                <p>该章节暂无内容，请检查章节生成是否成功。</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 剧情分支显示 */}
      {showBranches && plotBranches.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">剧情分支选择</h2>
            <button
              className="text-gray-500 hover:text-gray-700"
              onClick={() => setShowBranches(false)}
            >
              ✕
            </button>
          </div>

          <p className="text-gray-600 mb-4">
            以下是为当前章节生成的不同剧情发展方向，您可以选择其中一个继续故事：
          </p>

          <div className="space-y-4">
            {plotBranches.map((branch, index) => (
              <div key={index} className="p-4 border rounded-lg hover:bg-gray-50">
                <h3 className="font-medium mb-2">分支 {index + 1}: {branch.title || `选项${index + 1}`}</h3>
                <p className="text-gray-700 mb-3">{branch.description || branch.content}</p>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    影响程度: {branch.impact_level || '中等'}
                  </span>
                  <button
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                    onClick={() => {
                      toast.success('已选择剧情分支，将在下一章中体现');
                      setShowBranches(false);
                    }}
                  >
                    选择此分支
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

export default ChapterDetailPage;
