import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { charactersApi } from '../api';

const CharacterDetailPage: React.FC = () => {
  const { projectId, characterId } = useParams<{ projectId: string; characterId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [characterSet, setCharacterSet] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editedContent, setEditedContent] = useState<string>('');
  const [selectedCharacterIndex, setSelectedCharacterIndex] = useState<number>(0);
  const [charactersList, setCharactersList] = useState<any[]>([]);

  useEffect(() => {
    if (projectId && characterId) {
      fetchCharacter();
    }
  }, [projectId, characterId]);

  useEffect(() => {
    // 从URL参数获取要显示的人物索引
    const characterIndex = searchParams.get('characterIndex');
    if (characterIndex !== null) {
      setSelectedCharacterIndex(parseInt(characterIndex, 10));
    }
  }, [searchParams]);

  const fetchCharacter = async () => {
    try {
      setLoading(true);
      const charactersData = await charactersApi.getCharacters(projectId!);
      const characterData = charactersData.find((char: any) => char.id === characterId);

      if (!characterData) {
        toast.error('人物设定集不存在');
        navigate(`/projects/${projectId}/characters`);
        return;
      }

      setCharacterSet(characterData);

      // 解析人物列表
      const characters = extractCharactersList(characterData.content);
      setCharactersList(characters);

      // 设置初始编辑内容
      if (characters.length > selectedCharacterIndex) {
        const selectedChar = characters[selectedCharacterIndex];
        setEditedContent(JSON.stringify(selectedChar, null, 2));
      }

      setLoading(false);
    } catch (error) {
      console.error('获取人物详情失败:', error);
      toast.error('获取人物详情失败');
      setLoading(false);
    }
  };

  // 从人物设定集中提取人物列表
  const extractCharactersList = (content: any): any[] => {
    if (!content) return [];

    // 如果content有characters数组
    if (content.characters && Array.isArray(content.characters)) {
      return content.characters;
    }

    // 如果content有人物设定字段（中文）
    if (content.人物设定 && Array.isArray(content.人物设定)) {
      return content.人物设定;
    }

    // 如果content是字符串，尝试解析
    if (typeof content === 'string') {
      try {
        const parsed = JSON.parse(content);
        return extractCharactersList(parsed);
      } catch {
        return [{ name: '未命名角色', content: content }];
      }
    }

    // 如果没有找到结构化的人物数据，返回整个content作为单个人物
    return [content];
  };

  const handleSaveEdit = async () => {
    try {
      // 尝试解析为JSON，如果失败则保存为字符串
      let parsedContent;
      try {
        parsedContent = JSON.parse(editedContent);
      } catch {
        parsedContent = editedContent;
      }

      // 更新人物列表中的对应人物
      const updatedCharacters = [...charactersList];
      updatedCharacters[selectedCharacterIndex] = parsedContent;

      // 重新构建人物设定集内容
      let updatedContent = { ...characterSet.content };
      if (updatedContent.characters) {
        updatedContent.characters = updatedCharacters;
      } else if (updatedContent.人物设定) {
        updatedContent.人物设定 = updatedCharacters;
      } else {
        updatedContent = { characters: updatedCharacters };
      }

      await charactersApi.updateCharacter(projectId!, characterId!, {
        content: updatedContent
      });

      setCharacterSet({ ...characterSet, content: updatedContent });
      setCharactersList(updatedCharacters);
      setEditMode(false);
      toast.success('人物设定保存成功');
    } catch (error) {
      console.error('保存人物设定失败:', error);
      toast.error('保存人物设定失败');
    }
  };

  const handleCancelEdit = () => {
    // 重置编辑内容
    if (charactersList.length > selectedCharacterIndex) {
      const selectedChar = charactersList[selectedCharacterIndex];
      setEditedContent(JSON.stringify(selectedChar, null, 2));
    }
    setEditMode(false);
  };

  const getCharacterName = (character: any, index?: number) => {
    if (!character) return `角色${(index || 0) + 1}`;

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

    // 如果是字符串，尝试从中提取
    if (typeof character === 'string') {
      const nameMatch = character.match(/(?:姓名|名字|Name)[：:]\s*([^\s,，。\n]+)/);
      if (nameMatch) return nameMatch[1];
    }

    return `角色${(index || 0) + 1}`;
  };

  const renderSingleCharacterContent = (character: any) => {
    if (!character) return <p className="text-gray-500">暂无内容</p>;

    // 如果character是字符串，直接显示
    if (typeof character === 'string') {
      return (
        <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
          {character}
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* 基本信息 */}
        {character.基本信息 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">基本信息</h4>
            <div className="text-gray-600">
              {typeof character.基本信息 === 'object' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(character.基本信息).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex">
                      <span className="font-medium text-gray-700 w-20">{key}:</span>
                      <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p>{character.基本信息}</p>
              )}
            </div>
          </div>
        )}

        {/* 英文基本信息 */}
        {character.basic_info && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">基本信息</h4>
            <div className="text-gray-600">
              {typeof character.basic_info === 'object' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(character.basic_info).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex">
                      <span className="font-medium text-gray-700 w-20">{key}:</span>
                      <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p>{character.basic_info}</p>
              )}
            </div>
          </div>
        )}

        {/* 背景故事 */}
        {character.背景故事 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">背景故事</h4>
            <p className="text-gray-600 leading-relaxed">{character.背景故事}</p>
          </div>
        )}

        {/* 英文背景故事 */}
        {character.background && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">背景故事</h4>
            <p className="text-gray-600 leading-relaxed">{character.background}</p>
          </div>
        )}

        {/* 性格特质 */}
        {character.性格特质 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">性格特质</h4>
            <div className="text-gray-600">
              {typeof character.性格特质 === 'object' ? (
                <div className="space-y-2">
                  {Object.entries(character.性格特质).map(([key, value]: [string, any]) => (
                    <div key={key} className="flex">
                      <span className="font-medium text-gray-700 w-24">{key}:</span>
                      <span>{Array.isArray(value) ? value.join(', ') : String(value)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p>{character.性格特质}</p>
              )}
            </div>
          </div>
        )}

        {/* 英文性格特质 */}
        {character.personality && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">性格特质</h4>
            <p className="text-gray-600 leading-relaxed">{character.personality}</p>
          </div>
        )}

        {/* 角色弧光 */}
        {character.角色弧光 && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">角色弧光</h4>
            <p className="text-gray-600 leading-relaxed">{character.角色弧光}</p>
          </div>
        )}

        {/* 英文角色弧光 */}
        {character.arc && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">角色弧光</h4>
            <p className="text-gray-600 leading-relaxed">{character.arc}</p>
          </div>
        )}

        {/* 能力技能 */}
        {character.abilities && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">能力技能</h4>
            <p className="text-gray-600 leading-relaxed">{character.abilities}</p>
          </div>
        )}

        {/* 人际关系 */}
        {character.relationships && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">人际关系</h4>
            <p className="text-gray-600 leading-relaxed">{character.relationships}</p>
          </div>
        )}

        {/* 其他字段 */}
        {Object.entries(character).map(([key, value]: [string, any]) => {
          // 跳过已经显示的字段
          const displayedFields = ['基本信息', 'basic_info', '背景故事', 'background', '性格特质', 'personality', '角色弧光', 'arc', 'abilities', 'relationships', 'name'];
          if (displayedFields.includes(key) || !value) return null;

          return (
            <div key={key} className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-800 mb-3">{key}</h4>
              <div className="text-gray-600 leading-relaxed">
                {typeof value === 'object' ? (
                  <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(value, null, 2)}</pre>
                ) : (
                  <p>{String(value)}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (!characterSet || charactersList.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">人物设定集不存在或为空</p>
          <button
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={() => navigate(`/projects/${projectId}/characters`)}
          >
            返回人物列表
          </button>
        </div>
      </div>
    );
  }

  const currentCharacter = charactersList[selectedCharacterIndex] || charactersList[0];
  const characterName = getCharacterName(currentCharacter, selectedCharacterIndex);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* 头部导航 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <button
              className="mr-4 px-3 py-1 text-blue-600 hover:text-blue-800 transition-colors"
              onClick={() => navigate(`/projects/${projectId}/characters`)}
            >
              ← 返回人物列表
            </button>
            <h1 className="text-2xl font-bold text-gray-900">
              {characterName}
            </h1>
          </div>

          <div className="flex space-x-2">
            {editMode ? (
              <>
                <button
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                  onClick={handleSaveEdit}
                >
                  保存
                </button>
                <button
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                  onClick={handleCancelEdit}
                >
                  取消
                </button>
              </>
            ) : (
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                onClick={() => setEditMode(true)}
              >
                编辑
              </button>
            )}
          </div>
        </div>

        {/* 人物选择器 */}
        {charactersList.length > 1 && (
          <div className="bg-white p-4 rounded-lg shadow-md mb-6">
            <h3 className="text-lg font-semibold mb-3">选择人物</h3>
            <div className="flex flex-wrap gap-2">
              {charactersList.map((char, index) => (
                <button
                  key={index}
                  className={`px-3 py-2 rounded-lg transition-colors ${
                    index === selectedCharacterIndex
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  onClick={() => {
                    setSelectedCharacterIndex(index);
                    if (!editMode) {
                      setEditedContent(JSON.stringify(char, null, 2));
                    }
                  }}
                >
                  {getCharacterName(char, index)}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 人物详情内容 */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          {editMode ? (
            <div>
              <h3 className="text-lg font-semibold mb-4">编辑人物设定 - {characterName}</h3>
              <p className="text-gray-600 mb-4">
                您可以直接编辑人物设定内容。支持纯文本或JSON格式。
              </p>
              <textarea
                className="w-full h-96 p-4 border rounded-lg font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                placeholder="请输入人物设定内容..."
              />
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-semibold mb-4">{characterName} - 详细设定</h3>
              {renderSingleCharacterContent(currentCharacter)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CharacterDetailPage;
