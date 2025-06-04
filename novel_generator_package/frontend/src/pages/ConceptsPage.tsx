import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsApi, conceptsApi } from '../api';
import { toast } from 'react-hot-toast';

const ConceptsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<any>(null);
  const [concepts, setConcepts] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [userInput, setUserInput] = useState<string>('');
  const [numConcepts, setNumConcepts] = useState<number>(3);
  const [expandingConceptId, setExpandingConceptId] = useState<string | null>(null);
  const [novelStyle, setNovelStyle] = useState<string>('');
  const [customStyle, setCustomStyle] = useState<string>('');
  const [editingConceptId, setEditingConceptId] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState<string>('');

  useEffect(() => {
    if (projectId) {
      fetchProjectAndConcepts();
    }
  }, [projectId]);

  const fetchProjectAndConcepts = async () => {
    try {
      setLoading(true);
      const projectData = await projectsApi.getProject(projectId!);
      setProject(projectData);
      
      const conceptsData = await conceptsApi.getConcepts(projectId!);
      setConcepts(conceptsData);
      
      setLoading(false);
    } catch (error) {
      console.error('获取数据失败:', error);
      toast.error('获取项目数据失败');
      setLoading(false);
    }
  };

  const handleGenerateConcepts = async () => {
    if (!userInput.trim()) {
      toast.error('请输入创作灵感或想法');
      return;
    }

    try {
      setGenerating(true);

      // 确定最终的风格
      const finalStyle = novelStyle === '自定义' ? customStyle : novelStyle;

      const result = await conceptsApi.generateConcepts(projectId!, {
        user_input: userInput,
        num_concepts: numConcepts,
        style_preference: finalStyle || null
      });

      // 处理响应数据，确保兼容性
      const conceptsData = result.concepts || result || [];
      setConcepts(conceptsData);
      toast.success('概述生成成功');
      setGenerating(false);
    } catch (error) {
      console.error('生成概述失败:', error);
      toast.error('生成概述失败');
      setGenerating(false);
    }
  };

  const handleSelectConcept = async (conceptId: string) => {
    try {
      const result = await conceptsApi.selectConcept(projectId!, conceptId);

      // 更新本地状态
      setConcepts(concepts.map(concept => ({
        ...concept,
        is_selected: concept.id === conceptId
      })));

      toast.success('已选择概述');

      // 刷新概述数据
      await fetchProjectAndConcepts();
    } catch (error) {
      console.error('选择概述失败:', error);
      toast.error('选择概述失败');
    }
  };

  const handleExpandConcept = async (conceptId: string) => {
    try {
      setExpandingConceptId(conceptId);
      const updatedConcept = await conceptsApi.expandConcept(projectId!, conceptId);
      
      // 更新本地状态
      setConcepts(concepts.map(concept => 
        concept.id === conceptId ? updatedConcept : concept
      ));
      
      toast.success('概述已扩展');
      setExpandingConceptId(null);
    } catch (error) {
      console.error('扩展概述失败:', error);
      toast.error('扩展概述失败');
      setExpandingConceptId(null);
    }
  };

  const handleEditConcept = (conceptId: string, content: string) => {
    setEditingConceptId(conceptId);
    setEditedContent(content);
  };

  const handleSaveConcept = async (conceptId: string) => {
    try {
      const result = await conceptsApi.updateConcept(projectId!, conceptId, {
        content: editedContent
      });

      // 更新本地状态
      setConcepts(concepts.map(concept =>
        concept.id === conceptId ? { ...concept, content: editedContent } : concept
      ));

      setEditingConceptId(null);
      setEditedContent('');
      toast.success('概述已保存');
    } catch (error) {
      console.error('保存概述失败:', error);
      toast.error('保存概述失败');
    }
  };

  const handleCancelEdit = () => {
    setEditingConceptId(null);
    setEditedContent('');
  };

  const handleContinue = () => {
    const selectedConcept = concepts.find(concept => concept.is_selected);
    if (!selectedConcept) {
      toast.error('请先选择一个概述');
      return;
    }

    navigate(`/projects/${projectId}/world-settings`);
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
        <h2 className="text-xl font-semibold mb-4">创作灵感</h2>
        <p className="text-gray-600 mb-4">
          请输入您的创作灵感、想法或关键词，AI将为您生成多个小说概述供选择
        </p>
        
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="userInput">
            创作灵感或想法 *
          </label>
          <textarea
            id="userInput"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="例如：一个发现自己拥有预知未来能力的普通高中生，在一次意外中看到了学校将要发生的灾难..."
            rows={4}
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
          />
        </div>

        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="novelStyle">
            小说风格类型 (可选)
          </label>
          <select
            id="novelStyle"
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline w-full"
            value={novelStyle}
            onChange={(e) => setNovelStyle(e.target.value)}
          >
            <option value="">请选择风格类型</option>
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
        </div>

        {novelStyle === '自定义' && (
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="customStyle">
              自定义风格描述
            </label>
            <input
              id="customStyle"
              type="text"
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              placeholder="请描述您想要的小说风格..."
              value={customStyle}
              onChange={(e) => setCustomStyle(e.target.value)}
            />
          </div>
        )}

        <div className="mb-6">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="numConcepts">
            生成概述数量
          </label>
          <select
            id="numConcepts"
            className="shadow border rounded py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            value={numConcepts}
            onChange={(e) => setNumConcepts(parseInt(e.target.value))}
          >
            <option value={1}>1个</option>
            <option value={2}>2个</option>
            <option value={3}>3个</option>
            <option value={5}>5个</option>
          </select>
        </div>
        
        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          onClick={handleGenerateConcepts}
          disabled={generating || !userInput.trim()}
        >
          {generating ? '生成中...' : '生成概述'}
        </button>
      </div>

      {concepts.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">小说概述</h2>
          <p className="text-gray-600 mb-4">
            请选择一个您喜欢的概述，然后点击"扩展"获取更详细的情节梗概
          </p>
          
          <div className="space-y-6">
            {concepts.map((concept) => (
              <div
                key={concept.id}
                className={`bg-white p-6 rounded-lg shadow-md border-2 ${
                  concept.is_selected ? 'border-blue-500' : 'border-transparent'
                }`}
              >
                {/* 质量评估 */}
                {concept.quality_score && (
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-blue-800">质量评分</span>
                      <span className="text-2xl font-bold text-blue-600">{concept.quality_score}/10</span>
                    </div>
                    {concept.recommendation_reason && (
                      <p className="text-sm text-blue-700">{concept.recommendation_reason}</p>
                    )}
                  </div>
                )}

                {editingConceptId === concept.id ? (
                  <div className="mb-4">
                    <textarea
                      className="w-full h-32 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={editedContent}
                      onChange={(e) => setEditedContent(e.target.value)}
                    />
                  </div>
                ) : (
                  <div className="whitespace-pre-wrap mb-4">
                    {concept.content}
                  </div>
                )}
                
                {concept.expanded_content && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-semibold mb-2">详细情节梗概:</h4>
                    <div className="whitespace-pre-wrap">
                      {concept.expanded_content}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end space-x-2 mt-4">
                  {editingConceptId === concept.id ? (
                    <>
                      <button
                        className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        onClick={handleCancelEdit}
                      >
                        取消
                      </button>
                      <button
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        onClick={() => handleSaveConcept(concept.id)}
                      >
                        保存
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        className={`px-4 py-2 rounded-lg transition-colors ${
                          concept.is_selected
                            ? 'bg-gray-200 text-gray-700'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                        onClick={() => handleSelectConcept(concept.id)}
                        disabled={concept.is_selected}
                      >
                        {concept.is_selected ? '已选择' : '选择'}
                      </button>

                      <button
                        className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                        onClick={() => handleEditConcept(concept.id, concept.content)}
                      >
                        编辑
                      </button>

                      <button
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
                        onClick={() => handleExpandConcept(concept.id)}
                        disabled={!!expandingConceptId || !!concept.expanded_content}
                      >
                        {expandingConceptId === concept.id ? '扩展中...' : concept.expanded_content ? '已扩展' : '扩展'}
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

export default ConceptsPage;
