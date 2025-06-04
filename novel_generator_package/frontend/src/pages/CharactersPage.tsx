import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsApi, charactersApi, plotOutlinesApi, worldSettingsApi, conceptsApi } from '../api';
import { toast } from 'react-hot-toast';

const CharactersPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<any>(null);
  const [selectedConcept, setSelectedConcept] = useState<any>(null);
  const [selectedWorldSetting, setSelectedWorldSetting] = useState<any>(null);
  const [selectedPlotOutline, setSelectedPlotOutline] = useState<any>(null);
  const [characters, setCharacters] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [numProfiles, setNumProfiles] = useState<number>(1);


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
      
      // 获取已选择的大纲
      const plotOutlinesData = await plotOutlinesApi.getPlotOutlines(projectId!);
      const selectedOutlineData = plotOutlinesData.find((outline: any) => outline.is_selected);
      
      if (!selectedOutlineData) {
        toast.error('请先选择一个大纲');
        navigate(`/projects/${projectId}/plot-outlines`);
        return;
      }
      
      setSelectedPlotOutline(selectedOutlineData);
      
      // 获取人物设定
      const charactersData = await charactersApi.getCharacters(projectId!);
      setCharacters(charactersData);
      
      setLoading(false);
    } catch (error) {
      console.error('获取数据失败:', error);
      toast.error('获取项目数据失败');
      setLoading(false);
    }
  };

  const handleGenerateCharacters = async () => {
    if (!selectedConcept || !selectedWorldSetting || !selectedPlotOutline) {
      toast.error('请先完成前面的步骤');
      return;
    }

    try {
      setGenerating(true);
      
      // 使用选定的概述、世界观设定和大纲生成人物设定
      const narrativeContent = selectedConcept.expanded_content || selectedConcept.content;
      
      const result = await charactersApi.generateCharacters(projectId!, {
        num_character_sets: numProfiles
      });
      
      // 处理响应数据，确保兼容性
      const charactersData = result.characters || result || [];
      setCharacters(charactersData);
      toast.success('人物设定生成成功');
      setGenerating(false);
    } catch (error) {
      console.error('生成人物设定失败:', error);
      toast.error('生成人物设定失败');
      setGenerating(false);
    }
  };

  const handleSelectCharacter = async (characterId: string) => {
    try {
      await charactersApi.selectCharacter(projectId!, characterId);

      // 更新本地状态
      setCharacters(characters.map(character => ({
        ...character,
        is_selected: character.id === characterId
      })));

      toast.success('已选择人物设定');
    } catch (error) {
      console.error('选择人物设定失败:', error);
      toast.error('选择人物设定失败');
    }
  };



  const handleContinue = () => {
    const selectedCharacter = characters.find(character => character.is_selected);
    if (!selectedCharacter) {
      toast.error('请先选择一个人物设定');
      return;
    }

    navigate(`/projects/${projectId}/chapters`);
  };

  // 提取人物名字列表的函数
  const getCharacterNames = (character: any) => {
    const content = character.content;
    if (!content) return ['未命名角色'];

    // 如果content是字符串，尝试从中提取姓名
    if (typeof content === 'string') {
      const nameMatch = content.match(/(?:姓名|名字|Name)[：:]\s*([^\s,，。\n]+)/);
      if (nameMatch) return [nameMatch[1]];
      return ['未命名角色'];
    }

    // 如果content有characters数组
    if (content.characters && Array.isArray(content.characters)) {
      return content.characters.map((char: any, index: number) => {
        if (char.name) return char.name;
        if (char.基本信息?.姓名) return char.基本信息.姓名;
        if (char.basic_info?.姓名) return char.basic_info.姓名;
        if (char.basic_info?.name) return char.basic_info.name;

        // 如果basic_info是字符串，尝试从中提取姓名
        if (typeof char.basic_info === 'string') {
          const nameMatch = char.basic_info.match(/(?:姓名|名字)[：:]\s*([^\s,，。]+)/);
          if (nameMatch) return nameMatch[1];
        }

        return `角色${index + 1}`;
      });
    }

    // 如果content有人物设定字段
    if (content.人物设定 && Array.isArray(content.人物设定)) {
      return content.人物设定.map((char: any, index: number) => {
        if (char.基本信息?.姓名) return char.基本信息.姓名;
        if (char.name) return char.name;
        return `角色${index + 1}`;
      });
    }

    return ['未命名角色'];
  };

  const renderCharacterSummary = (character: any) => {
    const names = getCharacterNames(character);
    const content = character.content;

    return (
      <div>
        <h4 className="font-semibold mb-2">人物设定集 {character.id}</h4>
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">包含人物：</p>
          <div className="flex flex-wrap gap-2">
            {names.map((name, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm cursor-pointer hover:bg-blue-200 transition-colors"
                onClick={() => navigate(`/projects/${projectId}/characters/${character.id}`)}
              >
                {name}
              </span>
            ))}
          </div>
        </div>

        {/* 简要描述 */}
        <div className="text-gray-600 text-sm">
          {typeof content === 'string' ? (
            <p>{content.substring(0, 150)}...</p>
          ) : (
            <p>包含 {names.length} 个人物的详细设定</p>
          )}
        </div>
      </div>
    );
  };

  const renderCharacterContent = (character: any) => {
    const content = character.content;
    if (!content) return <p className="text-gray-500">暂无内容</p>;

    // 如果content是字符串，直接显示
    if (typeof content === 'string') {
      return (
        <div>
          <h4 className="font-semibold mb-4">人物设定内容</h4>
          <div className="whitespace-pre-wrap text-gray-700">{content}</div>
        </div>
      );
    }

    // 如果content有characters数组，按结构化方式显示
    if (content.characters && Array.isArray(content.characters)) {
      return (
        <div>
          <h4 className="font-semibold mb-4">人物设定集 {content.set_number || '1'}</h4>

          <div className="space-y-8">
            {content.characters.map((char: any, index: number) => {
              // 提取人物姓名的逻辑
              const getCharacterName = (character: any) => {
                // 直接的name字段
                if (character.name) return character.name;

                // 中文结构化数据
                if (character.基本信息?.姓名) return character.基本信息.姓名;

                // 英文结构化数据
                if (character.basic_info?.姓名) return character.basic_info.姓名;
                if (character.basic_info?.name) return character.basic_info.name;

                // 如果basic_info是字符串，尝试从中提取姓名
                if (typeof character.basic_info === 'string') {
                  const nameMatch = character.basic_info.match(/(?:姓名|名字)[：:]\s*([^\s,，。]+)/);
                  if (nameMatch) return nameMatch[1];
                }

                // 如果是JSON字符串，尝试解析
                if (typeof character === 'string') {
                  try {
                    const parsed = JSON.parse(character);
                    return getCharacterName(parsed);
                  } catch (e) {
                    // 如果解析失败，尝试从字符串中提取
                    const nameMatch = character.match(/(?:姓名|名字)[：:]\s*([^\s,，。]+)/);
                    if (nameMatch) return nameMatch[1];
                  }
                }

                return `角色${index + 1}`;
              };

              return (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-lg mb-3 text-blue-700">
                    {getCharacterName(char)}
                  </h5>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {char.basic_info && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">基本信息:</p>
                      <p className="text-gray-600">{char.basic_info}</p>
                    </div>
                  )}
                  {char.background && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">背景故事:</p>
                      <p className="text-gray-600">{char.background}</p>
                    </div>
                  )}
                  {char.personality && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">性格特质:</p>
                      <p className="text-gray-600">{char.personality}</p>
                    </div>
                  )}
                  {char.abilities && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">能力技能:</p>
                      <p className="text-gray-600">{char.abilities}</p>
                    </div>
                  )}
                  {char.motivations && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">动机与目标:</p>
                      <p className="text-gray-600">{char.motivations}</p>
                    </div>
                  )}
                  {char.arc && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">角色弧光:</p>
                      <p className="text-gray-600">{char.arc}</p>
                    </div>
                  )}
                  {char.relationships && (
                    <div className="md:col-span-2">
                      <p className="text-sm font-medium text-gray-700">人际关系:</p>
                      <p className="text-gray-600">{char.relationships}</p>
                    </div>
                  )}
                  {char.age && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">年龄:</p>
                      <p className="text-gray-600">{char.age}</p>
                    </div>
                  )}
                  {char.appearance && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">外貌:</p>
                      <p className="text-gray-600">{char.appearance}</p>
                    </div>
                  )}
                  {char.skills && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">技能:</p>
                      <p className="text-gray-600">{char.skills}</p>
                    </div>
                  )}
                </div>
              </div>
              );
            })}
          </div>
        </div>
      );
    }

    // 如果content有人物设定字段（中文）
    if (content.人物设定 && Array.isArray(content.人物设定)) {
      return (
        <div>
          <h4 className="font-semibold mb-4">人物设定详情</h4>
          <div className="space-y-8">
            {content.人物设定.map((char: any, index: number) => {
              const getCharacterName = (character: any) => {
                if (character.基本信息?.姓名) return character.基本信息.姓名;
                if (character.name) return character.name;
                return `角色${index + 1}`;
              };

              return (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <h5 className="font-medium text-lg mb-3 text-blue-700">
                    {getCharacterName(char)}
                  </h5>
                  <div className="space-y-3">
                    {char.基本信息 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">基本信息:</p>
                        <div className="text-gray-600">
                          {typeof char.基本信息 === 'object' ? (
                            <div className="grid grid-cols-2 gap-2">
                              {Object.entries(char.基本信息).map(([key, value]: [string, any]) => (
                                <div key={key}>
                                  <span className="font-medium">{key}:</span> {Array.isArray(value) ? value.join(', ') : value}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p>{char.基本信息}</p>
                          )}
                        </div>
                      </div>
                    )}
                    {char.背景故事 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">背景故事:</p>
                        <p className="text-gray-600">{char.背景故事}</p>
                      </div>
                    )}
                    {char.性格特质 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">性格特质:</p>
                        <div className="text-gray-600">
                          {typeof char.性格特质 === 'object' ? (
                            <div className="space-y-1">
                              {Object.entries(char.性格特质).map(([key, value]: [string, any]) => (
                                <div key={key}>
                                  <span className="font-medium">{key}:</span> {Array.isArray(value) ? value.join(', ') : value}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p>{char.性格特质}</p>
                          )}
                        </div>
                      </div>
                    )}
                    {char.角色弧光 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700">角色弧光:</p>
                        <p className="text-gray-600">{char.角色弧光}</p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          {content.人物关系图谱 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h5 className="font-medium text-blue-800 mb-2">人物关系图谱</h5>
              <p className="text-blue-700">{content.人物关系图谱}</p>
            </div>
          )}
        </div>
      );
    }

    // 如果没有结构化数据，显示原始内容
    return (
      <div>
        <h4 className="font-semibold mb-4">人物设定内容</h4>
        <div className="whitespace-pre-wrap text-gray-700">
          {content.description || JSON.stringify(content, null, 2)}
        </div>
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
        <h2 className="text-xl font-semibold mb-4">人物设定生成</h2>
        <p className="text-gray-600 mb-4">
          基于您选择的小说概述、世界观设定和大纲，AI将为您生成详细的人物设定
        </p>
        
        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="numProfiles">
            生成人物设定集数量
          </label>
          <select
            id="numProfiles"
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={numProfiles}
            onChange={(e) => setNumProfiles(parseInt(e.target.value))}
          >
            <option value={1}>1套</option>
            <option value={2}>2套</option>
            <option value={3}>3套</option>
            <option value={4}>4套</option>
            <option value={5}>5套</option>
          </select>
        </div>
        
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          onClick={handleGenerateCharacters}
          disabled={generating || !selectedConcept || !selectedWorldSetting || !selectedPlotOutline}
        >
          {generating ? '生成中...' : '生成人物设定'}
        </button>
      </div>

      {characters.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">人物设定</h2>
          <p className="text-gray-600 mb-4">
            请选择一个您喜欢的人物设定集，用于后续的小说创作。点击人物名字可以查看和编辑详情。
          </p>

          <div className="space-y-6">
            {characters.map((character) => (
              <div
                key={character.id}
                className={`bg-white p-6 rounded-lg shadow-md border-2 ${
                  character.is_selected ? 'border-blue-500' : 'border-transparent'
                }`}
              >
                {renderCharacterSummary(character)}

                <div className="flex justify-between mt-6">
                  <button
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    onClick={() => navigate(`/projects/${projectId}/characters/${character.id}`)}
                  >
                    查看详情
                  </button>
                  <button
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      character.is_selected
                        ? 'bg-gray-200 text-gray-700'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                    onClick={() => handleSelectCharacter(character.id)}
                    disabled={character.is_selected}
                  >
                    {character.is_selected ? '已选择' : '选择此人物设定'}
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


    </div>
  );
};

export default CharactersPage;
