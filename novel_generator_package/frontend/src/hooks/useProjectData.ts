import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsApi, conceptsApi, worldSettingsApi, plotOutlinesApi, charactersApi, chaptersApi } from '../api';
import { toast } from 'react-hot-toast';

interface ProjectData {
  project: any;
  concepts: any[];
  worldSettings: any[];
  plotOutlines: any[];
  characters: any[];
  chapters: any[];
  selectedConcept: any;
  selectedWorldSetting: any;
  selectedPlotOutline: any;
  selectedCharacter: any;
}

interface UseProjectDataReturn extends ProjectData {
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  updateProject: (data: any) => Promise<void>;
}

export const useProjectData = (projectId: string | undefined): UseProjectDataReturn => {
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [project, setProject] = useState<any>(null);
  const [concepts, setConcepts] = useState<any[]>([]);
  const [worldSettings, setWorldSettings] = useState<any[]>([]);
  const [plotOutlines, setPlotOutlines] = useState<any[]>([]);
  const [characters, setCharacters] = useState<any[]>([]);
  const [chapters, setChapters] = useState<any[]>([]);

  // 计算选中的项目
  const selectedConcept = concepts.find(concept => concept.is_selected);
  const selectedWorldSetting = worldSettings.find(setting => setting.is_selected);
  const selectedPlotOutline = plotOutlines.find(outline => outline.is_selected);
  const selectedCharacter = characters.find(character => character.is_selected);

  const fetchProjectData = useCallback(async () => {
    if (!projectId) {
      setError('项目ID不存在');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // 获取项目信息
      const projectData = await projectsApi.getProject(projectId);
      setProject(projectData);

      // 并行获取所有相关数据
      const [
        conceptsData,
        worldSettingsData,
        plotOutlinesData,
        charactersData,
        chaptersData
      ] = await Promise.allSettled([
        conceptsApi.getConcepts(projectId),
        worldSettingsApi.getWorldSettings(projectId),
        plotOutlinesApi.getPlotOutlines(projectId),
        charactersApi.getCharacters(projectId),
        chaptersApi.getChapters(projectId)
      ]);

      // 处理概述数据
      if (conceptsData.status === 'fulfilled') {
        const concepts = conceptsData.value || [];
        setConcepts(concepts);
      } else {
        console.error('获取概述失败:', conceptsData.reason);
        setConcepts([]);
      }

      // 处理世界观设定数据
      if (worldSettingsData.status === 'fulfilled') {
        const worldSettings = worldSettingsData.value || [];
        setWorldSettings(worldSettings);
      } else {
        console.error('获取世界观设定失败:', worldSettingsData.reason);
        setWorldSettings([]);
      }

      // 处理大纲数据
      if (plotOutlinesData.status === 'fulfilled') {
        const plotOutlines = plotOutlinesData.value || [];
        setPlotOutlines(plotOutlines);
      } else {
        console.error('获取大纲失败:', plotOutlinesData.reason);
        setPlotOutlines([]);
      }

      // 处理人物数据
      if (charactersData.status === 'fulfilled') {
        const characters = charactersData.value || [];
        setCharacters(characters);
      } else {
        console.error('获取人物设定失败:', charactersData.reason);
        setCharacters([]);
      }

      // 处理章节数据
      if (chaptersData.status === 'fulfilled') {
        setChapters(chaptersData.value || []);
      } else {
        console.error('获取章节失败:', chaptersData.reason);
        setChapters([]);
      }

      setLoading(false);
    } catch (error: any) {
      console.error('获取项目数据失败:', error);
      const errorMessage = error.message || '获取项目数据失败';
      setError(errorMessage);
      setLoading(false);
      
      // 如果是项目不存在的错误，跳转到项目列表
      if (error.message && error.message.includes('404')) {
        toast.error('项目不存在，正在跳转到项目列表');
        navigate('/projects');
      } else {
        toast.error(errorMessage);
      }
    }
  }, [projectId, navigate]);

  const updateProject = useCallback(async (data: any) => {
    if (!projectId) return;
    
    try {
      const updatedProject = await projectsApi.updateProject(projectId, data);
      setProject(updatedProject);
      toast.success('项目更新成功');
    } catch (error: any) {
      console.error('更新项目失败:', error);
      const errorMessage = error.message || '更新项目失败';
      toast.error(errorMessage);
      throw error;
    }
  }, [projectId]);

  useEffect(() => {
    fetchProjectData();
  }, [fetchProjectData]);

  return {
    loading,
    error,
    project,
    concepts,
    worldSettings,
    plotOutlines,
    characters,
    chapters,
    selectedConcept,
    selectedWorldSetting,
    selectedPlotOutline,
    selectedCharacter,
    refetch: fetchProjectData,
    updateProject
  };
};
