import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

interface TokenConfig {
  concept_max_tokens: number;
  concept_expand_max_tokens: number;
  world_setting_max_tokens: number;
  plot_outline_max_tokens: number;
  character_max_tokens: number;
  chapter_max_tokens: number;
  chapter_polish_max_tokens: number;
  plot_branches_max_tokens: number;
  agent_temperature: number;
  agent_top_p: number;
  default_chapter_length: number;
}

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    apiBaseUrl: 'http://localhost:8002/api',
    defaultWritingStyle: '详细生动',
    autoSave: true,
    maxChapters: 30,
    defaultGenreStyle: '',
    llmProvider: 'openai',
    temperature: 0.7,
    maxTokens: 2000
  });

  const [tokenConfig, setTokenConfig] = useState<TokenConfig>({
    concept_max_tokens: 6000,
    concept_expand_max_tokens: 8000,
    world_setting_max_tokens: 8000,
    plot_outline_max_tokens: 10000,
    character_max_tokens: 8000,
    chapter_max_tokens: 6000,
    chapter_polish_max_tokens: 8000,
    plot_branches_max_tokens: 4000,
    agent_temperature: 0.7,
    agent_top_p: 0.9,
    default_chapter_length: 3000
  });

  const [writingStyles, setWritingStyles] = useState<string[]>([
    '详细生动', '简洁明快', '诗意抒情', '悬疑紧张', '幽默风趣',
    '古典优雅', '现代都市', '科幻硬核', '奇幻史诗', '自定义'
  ]);

  const [customWritingStyle, setCustomWritingStyle] = useState<string>('');
  const [customGenreStyle, setCustomGenreStyle] = useState<string>('');

  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);

      // 从localStorage加载基础设置
      const savedSettings = localStorage.getItem('novel-generator-settings');
      if (savedSettings) {
        try {
          const parsed = JSON.parse(savedSettings);
          setSettings({ ...settings, ...parsed });
        } catch (error) {
          console.error('加载本地设置失败:', error);
        }
      }

      // 从API加载token配置
      const response = await fetch(`${settings.apiBaseUrl}/settings/token-config`);
      if (response.ok) {
        const config = await response.json();
        setTokenConfig(config);
      }

      // 加载写作风格列表
      const stylesResponse = await fetch(`${settings.apiBaseUrl}/settings/writing-styles`);
      if (stylesResponse.ok) {
        const styles = await stylesResponse.json();
        setWritingStyles(styles);
      }
    } catch (error) {
      console.error('加载设置失败:', error);
      toast.error('加载设置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    try {
      setSaving(true);

      // 保存基础设置到localStorage
      localStorage.setItem('novel-generator-settings', JSON.stringify(settings));

      // 保存token配置到API
      const response = await fetch(`${settings.apiBaseUrl}/settings/token-config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tokenConfig),
      });

      if (!response.ok) {
        throw new Error('保存token配置失败');
      }

      toast.success('设置已保存');
    } catch (error) {
      console.error('保存设置失败:', error);
      toast.error('保存设置失败');
    } finally {
      setSaving(false);
    }
  };

  const handleResetSettings = () => {
    const defaultSettings = {
      apiBaseUrl: 'http://localhost:8002/api',
      defaultWritingStyle: '详细生动',
      autoSave: true,
      maxChapters: 30,
      defaultGenreStyle: '',
      llmProvider: 'openai',
      temperature: 0.7,
      maxTokens: 2000
    };
    
    setSettings(defaultSettings);
    localStorage.removeItem('novel-generator-settings');
    toast.success('设置已重置');
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-gray-600">加载设置中...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">系统设置</h1>
        <p className="text-gray-600">配置小说生成器的各项参数</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-6">基础设置</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              API基础URL
            </label>
            <input
              type="text"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={settings.apiBaseUrl}
              onChange={(e) => setSettings({ ...settings, apiBaseUrl: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              默认写作风格
            </label>
            <select
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={settings.defaultWritingStyle}
              onChange={(e) => setSettings({ ...settings, defaultWritingStyle: e.target.value })}
            >
              {writingStyles.map((style) => (
                <option key={style} value={style}>{style}</option>
              ))}
            </select>
            {settings.defaultWritingStyle === '自定义' && (
              <div className="mt-2">
                <input
                  type="text"
                  className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  placeholder="请输入自定义写作风格..."
                  value={customWritingStyle}
                  onChange={(e) => setCustomWritingStyle(e.target.value)}
                />
              </div>
            )}
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              默认小说风格
            </label>
            <select
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={settings.defaultGenreStyle}
              onChange={(e) => setSettings({ ...settings, defaultGenreStyle: e.target.value })}
            >
              <option value="">请选择</option>
              <option value="诙谐幽默">诙谐幽默</option>
              <option value="热血奋斗">热血奋斗</option>
              <option value="惊悚恐怖">惊悚恐怖</option>
              <option value="都市传说">都市传说</option>
              <option value="历史">历史</option>
              <option value="玄幻">玄幻</option>
              <option value="虐恋">虐恋</option>
              <option value="校园生活">校园生活</option>
              <option value="科幻">科幻</option>
              <option value="悬疑推理">悬疑推理</option>
              <option value="武侠">武侠</option>
              <option value="言情">言情</option>
              <option value="自定义">自定义</option>
            </select>
            {settings.defaultGenreStyle === '自定义' && (
              <div className="mt-2">
                <input
                  type="text"
                  className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  placeholder="请输入自定义小说风格..."
                  value={customGenreStyle}
                  onChange={(e) => setCustomGenreStyle(e.target.value)}
                />
              </div>
            )}
          </div>
        </div>

        <div className="mt-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              最大章节数
            </label>
            <input
              type="number"
              min="5"
              max="100"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={settings.maxChapters}
              onChange={(e) => setSettings({ ...settings, maxChapters: parseInt(e.target.value) })}
            />
          </div>
        </div>

        <div className="mt-6">
          <label className="flex items-center">
            <input
              type="checkbox"
              className="mr-2"
              checked={settings.autoSave}
              onChange={(e) => setSettings({ ...settings, autoSave: e.target.checked })}
            />
            <span className="text-gray-700">自动保存</span>
          </label>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-6">AI模型设置</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              LLM提供商
            </label>
            <select
              className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={settings.llmProvider}
              onChange={(e) => setSettings({ ...settings, llmProvider: e.target.value })}
            >
              <option value="openai">OpenAI</option>
              <option value="claude">Claude</option>
              <option value="local">本地模型</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              创造性温度 ({tokenConfig.agent_temperature})
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              className="w-full"
              value={tokenConfig.agent_temperature}
              onChange={(e) => setTokenConfig({ ...tokenConfig, agent_temperature: parseFloat(e.target.value) })}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>保守</span>
              <span>创新</span>
            </div>
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Top-P ({tokenConfig.agent_top_p})
            </label>
            <input
              type="range"
              min="0.1"
              max="1"
              step="0.1"
              className="w-full"
              value={tokenConfig.agent_top_p}
              onChange={(e) => setTokenConfig({ ...tokenConfig, agent_top_p: parseFloat(e.target.value) })}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>精确</span>
              <span>多样</span>
            </div>
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              默认章节长度
            </label>
            <input
              type="number"
              min="1000"
              max="10000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.default_chapter_length}
              onChange={(e) => setTokenConfig({ ...tokenConfig, default_chapter_length: parseInt(e.target.value) })}
            />
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-6">Token配置</h2>
        <p className="text-gray-600 mb-6">调整各个生成环节的最大Token数量，影响生成内容的长度和详细程度</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              概述生成
            </label>
            <input
              type="number"
              min="1000"
              max="20000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.concept_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, concept_max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              概述扩展
            </label>
            <input
              type="number"
              min="2000"
              max="20000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.concept_expand_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, concept_expand_max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              世界观设定
            </label>
            <input
              type="number"
              min="2000"
              max="20000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.world_setting_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, world_setting_max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              大纲生成
            </label>
            <input
              type="number"
              min="3000"
              max="30000"
              step="1000"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.plot_outline_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, plot_outline_max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              人物设定
            </label>
            <input
              type="number"
              min="2000"
              max="20000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.character_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, character_max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              章节生成
            </label>
            <input
              type="number"
              min="2000"
              max="20000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.chapter_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, chapter_max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              章节润色
            </label>
            <input
              type="number"
              min="2000"
              max="20000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.chapter_polish_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, chapter_polish_max_tokens: parseInt(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              剧情分支
            </label>
            <input
              type="number"
              min="1000"
              max="10000"
              step="500"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              value={tokenConfig.plot_branches_max_tokens}
              onChange={(e) => setTokenConfig({ ...tokenConfig, plot_branches_max_tokens: parseInt(e.target.value) })}
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end space-x-4">
        <button
          className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          onClick={handleResetSettings}
        >
          重置设置
        </button>
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          onClick={handleSaveSettings}
          disabled={saving}
        >
          {saving ? '保存中...' : '保存设置'}
        </button>
      </div>
    </div>
  );
};

export default SettingsPage;
