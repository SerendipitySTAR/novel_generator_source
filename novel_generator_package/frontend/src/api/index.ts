// API 接口封装

const API_BASE_URL = 'http://localhost:8002/api';

// 通用错误处理函数
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

    // 添加详细的调试信息
    console.error('API请求失败:', {
      url: response.url,
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries())
    });

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
      console.error('错误详情:', errorData);
    } catch (e) {
      // 如果无法解析错误响应，使用默认错误消息
      console.error('无法解析错误响应:', e);
    }
    throw new Error(errorMessage);
  }
  return response.json();
};

// 项目相关接口
export const projectsApi = {
  // 创建项目
  createProject: async (data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 获取项目列表
  getProjects: async () => {
    const response = await fetch(`${API_BASE_URL}/projects`);
    return handleResponse(response);
  },

  // 获取项目详情
  getProject: async (projectId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`);
    return handleResponse(response);
  },

  // 更新项目
  updateProject: async (projectId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 删除项目
  deleteProject: async (projectId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },
};

// 概述相关接口
export const conceptsApi = {
  // 生成概述
  generateConcepts: async (projectId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/concepts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 获取概述列表
  getConcepts: async (projectId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/concepts`);
    const result = await handleResponse(response);
    return result.concepts || [];
  },

  // 获取概述详情
  getConcept: async (projectId: string, conceptId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/concepts/${conceptId}`);
    return handleResponse(response);
  },

  // 选择概述
  selectConcept: async (projectId: string, conceptId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/concepts/${conceptId}/select`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    return handleResponse(response);
  },

  // 更新概述（保留兼容性）
  updateConcept: async (projectId: string, conceptId: string, data: any) => {
    // 如果是选择操作，使用新的选择接口
    if (data.is_selected) {
      return conceptsApi.selectConcept(projectId, conceptId);
    }

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/concepts/${conceptId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 扩展概述
  expandConcept: async (projectId: string, conceptId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/concepts/${conceptId}/expand`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    return handleResponse(response);
  },
};

// 世界观设定相关接口
export const worldSettingsApi = {
  // 生成世界观设定
  generateWorldSettings: async (projectId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/world-settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 获取世界观设定列表
  getWorldSettings: async (projectId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/world-settings`);
    const result = await handleResponse(response);
    return result.world_settings || [];
  },

  // 获取世界观设定详情
  getWorldSetting: async (projectId: string, settingId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/world-settings/${settingId}`);
    return handleResponse(response);
  },

  // 选择世界观设定
  selectWorldSetting: async (projectId: string, settingId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/world-settings/${settingId}/select`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    return handleResponse(response);
  },

  // 更新世界观设定
  updateWorldSetting: async (projectId: string, settingId: string, data: any) => {
    // 如果是选择操作，使用新的选择接口
    if (data.is_selected) {
      return worldSettingsApi.selectWorldSetting(projectId, settingId);
    }

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/world-settings/${settingId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
};

// 大纲相关接口
export const plotOutlinesApi = {
  // 生成大纲
  generatePlotOutlines: async (projectId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/plot-outlines`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 获取大纲列表
  getPlotOutlines: async (projectId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/plot-outlines`);
    const result = await handleResponse(response);
    return result.plot_outlines || [];
  },

  // 获取大纲详情
  getPlotOutline: async (projectId: string, outlineId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/plot-outlines/${outlineId}`);
    return handleResponse(response);
  },

  // 选择大纲
  selectPlotOutline: async (projectId: string, outlineId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/plot-outlines/${outlineId}/select`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    return handleResponse(response);
  },

  // 更新大纲
  updatePlotOutline: async (projectId: string, outlineId: string, data: any) => {
    // 如果是选择操作，使用新的选择接口
    if (data.is_selected) {
      return plotOutlinesApi.selectPlotOutline(projectId, outlineId);
    }

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/plot-outlines/${outlineId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
};

// 人物相关接口
export const charactersApi = {
  // 生成人物设定
  generateCharacters: async (projectId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/characters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 获取人物设定列表
  getCharacters: async (projectId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/characters`);
    const result = await handleResponse(response);
    return result.characters || result || [];
  },

  // 获取人物设定详情
  getCharacter: async (projectId: string, characterId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/characters/${characterId}`);
    return handleResponse(response);
  },

  // 选择人物设定
  selectCharacter: async (projectId: string, characterId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/characters/${characterId}/select`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    return handleResponse(response);
  },

  // 更新人物设定
  updateCharacter: async (projectId: string, characterId: string, data: any) => {
    // 如果是选择操作，使用新的选择接口
    if (data.is_selected) {
      return charactersApi.selectCharacter(projectId, characterId);
    }

    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/characters/${characterId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },
};

// 章节相关接口
export const chaptersApi = {
  // 生成章节内容
  generateChapter: async (projectId: string, data: any) => {
    const url = `${API_BASE_URL}/projects/${projectId}/chapters`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分钟超时

    // 添加详细的请求日志
    console.log('发送章节生成请求:', {
      url,
      method: 'POST',
      projectId,
      data
    });

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal,
      });

      console.log('章节生成响应:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });

      clearTimeout(timeoutId);
      return handleResponse(response);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('章节生成超时，请稍后重试');
      }
      throw error;
    }
  },

  // 生成剧情分支
  generatePlotBranches: async (projectId: string, chapterId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/chapters/${chapterId}/branches`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 获取章节列表
  getChapters: async (projectId: string) => {
    console.log('获取章节列表，项目ID:', projectId);
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/chapters`);
    console.log('章节列表响应状态:', response.status);
    const result = await handleResponse(response);
    console.log('章节列表原始响应:', result);

    // 新API直接返回章节数组，旧API返回 {chapters: [...]}
    const chapters = Array.isArray(result) ? result : (result.chapters || []);
    console.log('处理后的章节列表:', chapters);
    return chapters;
  },

  // 获取章节详情
  getChapter: async (projectId: string, chapterId: string) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/chapters/${chapterId}`);
    return handleResponse(response);
  },

  // 更新章节
  updateChapter: async (projectId: string, chapterId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/chapters/${chapterId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 润色章节
  polishChapter: async (projectId: string, chapterId: string, data: any) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/chapters/${chapterId}/polish`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  // 生成章节内容（带质量检查）
  generateChapterWithQualityCheck: async (projectId: string, data: any) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分钟超时

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/chapters/generate-with-quality-check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return handleResponse(response);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('章节生成超时，请稍后重试');
      }
      throw error;
    }
  },
};
