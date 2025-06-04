import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { charactersApi } from '../api';

const CharacterDetailPage: React.FC = () => {
  const { projectId, characterId } = useParams<{ projectId: string; characterId: string }>();
  const navigate = useNavigate();
  
  const [character, setCharacter] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editedContent, setEditedContent] = useState<string>('');

  useEffect(() => {
    if (projectId && characterId) {
      fetchCharacter();
    }
  }, [projectId, characterId]);

  const fetchCharacter = async () => {
    try {
      setLoading(true);
      const charactersData = await charactersApi.getCharacters(projectId!);
      const characterData = charactersData.find((char: any) => char.id === characterId);
      
      if (!characterData) {
        toast.error('人物不存在');
        navigate(`/projects/${projectId}/characters`);
        return;
      }
      
      setCharacter(characterData);
      
      // 将内容转换为可编辑的字符串格式
      const contentStr = typeof characterData.content === 'string'
        ? characterData.content
        : JSON.stringify(characterData.content, null, 2);
      setEditedContent(contentStr);
      
      setLoading(false);
    } catch (error) {
      console.error('获取人物详情失败:', error);
      toast.error('获取人物详情失败');
      setLoading(false);
    }
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

      await charactersApi.updateCharacter(projectId!, characterId!, {
        content: parsedContent
      });

      setCharacter({ ...character, content: parsedContent });
      setEditMode(false);
      toast.success('人物设定保存成功');
    } catch (error) {
      console.error('保存人物设定失败:', error);
      toast.error('保存人物设定失败');
    }
  };

  const handleCancelEdit = () => {
    // 重置编辑内容
    const contentStr = typeof character.content === 'string'
      ? character.content
      : JSON.stringify(character.content, null, 2);
    setEditedContent(contentStr);
    setEditMode(false);
  };

  const getCharacterName = (character: any) => {
    const content = character.content;
    if (!content) return '未命名角色';

    // 如果content是字符串，尝试从中提取姓名
    if (typeof content === 'string') {
      const nameMatch = content.match(/(?:姓名|名字|Name)[：:]\s*([^\s,，。\n]+)/);
      if (nameMatch) return nameMatch[1];
      return '未命名角色';
    }

    // 如果content有characters数组
    if (content.characters && Array.isArray(content.characters) && content.characters.length > 0) {
      const firstChar = content.characters[0];
      if (firstChar.name) return firstChar.name;
      if (firstChar.基本信息?.姓名) return firstChar.基本信息.姓名;
      if (firstChar.basic_info?.姓名) return firstChar.basic_info.姓名;
      if (firstChar.basic_info?.name) return firstChar.basic_info.name;
    }

    // 如果content有人物设定字段
    if (content.人物设定 && Array.isArray(content.人物设定) && content.人物设定.length > 0) {
      const firstChar = content.人物设定[0];
      if (firstChar.基本信息?.姓名) return firstChar.基本信息.姓名;
      if (firstChar.name) return firstChar.name;
    }

    return '未命名角色';
  };

  const renderCharacterContent = (character: any) => {
    const content = character.content;
    if (!content) return <p className="text-gray-500">暂无内容</p>;

    // 如果content是字符串，直接显示
    if (typeof content === 'string') {
      return (
        <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
          {content}
        </div>
      );
    }

    // 如果content有characters数组，按结构化方式显示
    if (content.characters && Array.isArray(content.characters)) {
      return (
        <div className="space-y-8">
          {content.characters.map((char: any, index: number) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <h5 className="font-medium text-lg mb-3 text-blue-700">
                {char.name || char.基本信息?.姓名 || `角色${index + 1}`}
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
              </div>
            </div>
          ))}
        </div>
      );
    }

    // 如果content有人物设定字段（中文）
    if (content.人物设定 && Array.isArray(content.人物设定)) {
      return (
        <div className="space-y-8">
          {content.人物设定.map((char: any, index: number) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <h5 className="font-medium text-lg mb-3 text-blue-700">
                {char.基本信息?.姓名 || char.name || `角色${index + 1}`}
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
          ))}
          {content.人物关系图谱 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h5 className="font-medium text-blue-800 mb-2">人物关系图谱</h5>
              <p className="text-blue-700">{content.人物关系图谱}</p>
            </div>
          )}
        </div>
      );
    }

    // 其他格式的内容，尝试以JSON格式显示
    return (
      <pre className="whitespace-pre-wrap text-gray-700 text-sm bg-gray-50 p-4 rounded-lg overflow-x-auto">
        {JSON.stringify(content, null, 2)}
      </pre>
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

  if (!character) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">人物不存在</p>
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
              {getCharacterName(character)}
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

        {/* 人物详情内容 */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          {editMode ? (
            <div>
              <h3 className="text-lg font-semibold mb-4">编辑人物设定</h3>
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
              <h3 className="text-lg font-semibold mb-4">人物设定详情</h3>
              {renderCharacterContent(character)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CharacterDetailPage;
