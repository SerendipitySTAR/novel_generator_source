import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { worldSettingsApi } from '../api';
import { useProjectData } from '../hooks/useProjectData';
import DebugInfo from '../components/DebugInfo';
import { toast } from 'react-hot-toast';

const WorldSettingsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const {
    loading,
    error,
    project,
    selectedConcept,
    worldSettings,
    refetch
  } = useProjectData(projectId);

  const [generating, setGenerating] = useState<boolean>(false);
  const [numSettings, setNumSettings] = useState<number>(3);
  const [localWorldSettings, setLocalWorldSettings] = useState<any[]>([]);
  const [editingSettingId, setEditingSettingId] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState<any>(null);

  // 使用本地状态来管理世界观设定，以便实时更新
  React.useEffect(() => {
    setLocalWorldSettings(worldSettings);
  }, [worldSettings]);

  // 检查是否需要跳转到概述页面
  React.useEffect(() => {
    if (!loading && !selectedConcept) {
      toast.error('请先选择一个小说概述');
      navigate(`/projects/${projectId}/concepts`);
    }
  }, [loading, selectedConcept, navigate, projectId]);

  const handleGenerateWorldSettings = async () => {
    if (!selectedConcept) {
      toast.error('请先选择一个小说概述');
      return;
    }

    try {
      setGenerating(true);

      // 使用选定的概述生成世界观设定
      const narrativeContent = selectedConcept.expanded_content || selectedConcept.content;

      const result = await worldSettingsApi.generateWorldSettings(projectId!, {
        narrative_concept: narrativeContent,
        num_settings: numSettings
      });

      setLocalWorldSettings(result.world_settings);
      toast.success('世界观设定生成成功');
      setGenerating(false);

      // 刷新数据
      await refetch();
    } catch (error: any) {
      console.error('生成世界观设定失败:', error);
      const errorMessage = error.message || '生成世界观设定失败';
      toast.error(errorMessage);
      setGenerating(false);
    }
  };

  const handleSelectWorldSetting = async (settingId: string) => {
    try {
      await worldSettingsApi.updateWorldSetting(projectId!, settingId, {
        is_selected: true
      });

      // 更新本地状态
      setLocalWorldSettings(localWorldSettings.map(setting => ({
        ...setting,
        is_selected: setting.id === settingId
      })));

      toast.success('已选择世界观设定');

      // 刷新数据
      await refetch();
    } catch (error: any) {
      console.error('选择世界观设定失败:', error);
      const errorMessage = error.message || '选择世界观设定失败';
      toast.error(errorMessage);
    }
  };

  const handleEditWorldSetting = (settingId: string, content: any) => {
    setEditingSettingId(settingId);
    setEditedContent({ ...content });
  };

  const handleSaveWorldSetting = async (settingId: string) => {
    try {
      await worldSettingsApi.updateWorldSetting(projectId!, settingId, {
        content: editedContent
      });

      // 更新本地状态
      setLocalWorldSettings(localWorldSettings.map(setting =>
        setting.id === settingId ? { ...setting, content: editedContent } : setting
      ));

      setEditingSettingId(null);
      setEditedContent(null);
      toast.success('世界观设定已保存');
    } catch (error) {
      console.error('保存世界观设定失败:', error);
      toast.error('保存世界观设定失败');
    }
  };

  const handleCancelEdit = () => {
    setEditingSettingId(null);
    setEditedContent(null);
  };

  const handleContinue = () => {
    const selectedSetting = localWorldSettings.find(setting => setting.is_selected);
    if (!selectedSetting) {
      toast.error('请先选择一个世界观设定');
      return;
    }

    navigate(`/projects/${projectId}/plot-outlines`);
  };

  const renderWorldSettingContent = (setting: any) => {
    const content = setting.content;
    if (!content) return null;

    const isEditing = editingSettingId === setting.id;

    if (isEditing) {
      return (
        <div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              世界观特色描述
            </label>
            <input
              type="text"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={editedContent?.description || ''}
              onChange={(e) => setEditedContent({ ...editedContent, description: e.target.value })}
            />
          </div>

          {Object.entries(editedContent?.sections || {}).map(([sectionName, sectionContent]: [string, any]) => (
            <div key={sectionName} className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">
                {sectionName}
              </label>
              <textarea
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                rows={4}
                value={sectionContent || ''}
                onChange={(e) => setEditedContent({
                  ...editedContent,
                  sections: {
                    ...editedContent.sections,
                    [sectionName]: e.target.value
                  }
                })}
              />
            </div>
          ))}
        </div>
      );
    }

    return (
      <div>
        <h4 className="font-semibold mb-2">世界观特色: {content.description}</h4>

        {Object.entries(content.sections || {}).map(([sectionName, sectionContent]: [string, any]) => (
          <div key={sectionName} className="mb-4">
            <h5 className="font-medium text-gray-800 mb-1">{sectionName}</h5>
            <p className="text-gray-700 whitespace-pre-wrap">{sectionContent}</p>
          </div>
        ))}
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

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              重试
            </button>
          </div>
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

      {/* 调试信息 */}
      <DebugInfo
        data={{
          projectId,
          loading,
          error,
          selectedConcept,
          worldSettingsCount: worldSettings.length,
          localWorldSettingsCount: localWorldSettings.length,
          worldSettings: worldSettings.slice(0, 2), // 只显示前2个避免太长
          localWorldSettings: localWorldSettings.slice(0, 2)
        }}
        title="调试信息"
      />

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">世界观设定生成</h2>
        <p className="text-gray-600 mb-4">
          基于您选择的小说概述，AI将为您生成多套详细、自洽的世界观设定
        </p>
        
        <div className="mb-6">
          <h3 className="font-semibold mb-2">已选择的小说概述:</h3>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="whitespace-pre-wrap">
              {selectedConcept?.expanded_content || selectedConcept?.content}
            </p>
          </div>
        </div>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="numSettings">
            生成世界观设定数量
          </label>
          <select
            id="numSettings"
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={numSettings}
            onChange={(e) => setNumSettings(parseInt(e.target.value))}
          >
            <option value={1}>1套</option>
            <option value={2}>2套</option>
            <option value={3}>3套</option>
          </select>
        </div>
        
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          onClick={handleGenerateWorldSettings}
          disabled={generating || !selectedConcept}
        >
          {generating ? '生成中...' : '生成世界观设定'}
        </button>
      </div>

      {localWorldSettings.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">世界观设定</h2>
          <p className="text-gray-600 mb-4">
            请选择一个您喜欢的世界观设定，用于后续的小说创作
          </p>

          <div className="space-y-6">
            {localWorldSettings.map((setting) => (
              <div
                key={setting.id}
                className={`bg-white p-6 rounded-lg shadow-md border-2 ${
                  setting.is_selected ? 'border-blue-500' : 'border-transparent'
                }`}
              >
                {renderWorldSettingContent(setting)}

                <div className="flex justify-end space-x-2 mt-4">
                  {editingSettingId === setting.id ? (
                    <>
                      <button
                        className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        onClick={handleCancelEdit}
                      >
                        取消
                      </button>
                      <button
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        onClick={() => handleSaveWorldSetting(setting.id)}
                      >
                        保存
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        className={`px-4 py-2 rounded-lg transition-colors ${
                          setting.is_selected
                            ? 'bg-gray-200 text-gray-700'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                        onClick={() => handleSelectWorldSetting(setting.id)}
                        disabled={setting.is_selected}
                      >
                        {setting.is_selected ? '已选择' : '选择此世界观'}
                      </button>

                      <button
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                        onClick={() => handleEditWorldSetting(setting.id, setting.content)}
                      >
                        编辑
                      </button>
                    </>
                  )}
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
    </div>
  );
};

export default WorldSettingsPage;
