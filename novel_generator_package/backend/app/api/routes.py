"""
API路由定义，提供小说生成器的HTTP接口
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import asyncio
import uuid

from app.db import get_db
from app.services import ProjectService, NovelGenerationService
from app.core.orchestration import NovelWorkflow
from app.core.llm import OpenAILLM
from app.core.knowledge_base import KnowledgeBase
from app.agents import (
    NarrativePathfinderAgent,
    WorldWeaverAgent,
    PlotArchitectAgent,
    CharacterSculptorAgent,
    ChapterChroniclerAgent,
    QualityGuardianAgent,
    ContentIntegrityAgent,
    ContextSynthesizerAgent,
    KnowledgeKeeperAgent,
    StylePolisherAgent
)

# 创建路由器
router = APIRouter(tags=["novel-generator"])

# 数据模型
class UserInput(BaseModel):
    prompt: str
    style_preference: Optional[str] = None
    genre_preference: Optional[str] = None
    num_concepts: Optional[int] = 3

class ConceptResponse(BaseModel):
    concepts: List[str]
    request_id: str

class ConceptSelection(BaseModel):
    concept_id: int
    request_id: str

class WorldSettingResponse(BaseModel):
    world_settings: List[Dict[str, Any]]
    request_id: str

class WorldSettingSelection(BaseModel):
    world_setting_id: int
    request_id: str

class PlotOutlineResponse(BaseModel):
    plot_outlines: List[Dict[str, Any]]
    request_id: str

class PlotOutlineSelection(BaseModel):
    plot_outline_id: int
    request_id: str

class CharacterProfilesResponse(BaseModel):
    character_profiles: List[Dict[str, Any]]
    request_id: str

class CharacterProfilesSelection(BaseModel):
    character_profiles_id: int
    request_id: str

class ChapterRequest(BaseModel):
    chapter_id: int
    request_id: str

class ChapterResponse(BaseModel):
    chapter_content: str
    chapter_id: int
    request_id: str

class BranchesResponse(BaseModel):
    plot_branches: List[Dict[str, Any]]
    chapter_id: int
    request_id: str

class BranchSelection(BaseModel):
    branch_id: int
    chapter_id: int
    request_id: str

# 内存存储（实际应用中应使用数据库）
projects = {}

# 依赖项
def get_workflow():
    llm = OpenAILLM()
    kb = KnowledgeBase()
    return NovelWorkflow(llm=llm, knowledge_base=kb)

# 路由定义
@router.post("/projects", response_model=Dict[str, str])
async def create_project():
    """创建新项目"""
    project_id = str(uuid.uuid4())
    projects[project_id] = {
        "status": "created",
        "data": {}
    }
    return {"project_id": project_id}

@router.post("/generate-concepts", response_model=ConceptResponse)
async def generate_concepts(
    user_input: UserInput,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """生成小说核心创意概述"""
    request_id = str(uuid.uuid4())
    
    # 创建概述智能体
    narrative_agent = NarrativePathfinderAgent(llm=workflow.llm)
    
    # 调用智能体生成概述
    result = await narrative_agent.run({
        "user_input": user_input.prompt,
        "num_concepts": user_input.num_concepts,
        "mode": "generate"
    })
    
    # 存储结果
    projects[request_id] = {
        "status": "concepts_generated",
        "data": {
            "user_input": user_input.model_dump(),
            "concepts": result["concepts"]
        }
    }
    
    return {
        "concepts": result["concepts"],
        "request_id": request_id
    }

@router.post("/select-concept", response_model=Dict[str, str])
async def select_concept(selection: ConceptSelection):
    """选择一个核心创意概述"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    if "concepts" not in project_data or selection.concept_id >= len(project_data["concepts"]):
        raise HTTPException(status_code=400, detail="Invalid concept selection")
    
    # 获取选定的概述
    selected_concept = project_data["concepts"][selection.concept_id]
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "concept_selected"
    projects[selection.request_id]["data"]["selected_concept"] = selected_concept
    
    return {"status": "success", "message": "Concept selected successfully"}

@router.post("/expand-concept", response_model=Dict[str, Any])
async def expand_concept(
    selection: ConceptSelection,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """扩展核心创意概述为详细情节梗概"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    if "concepts" not in project_data or selection.concept_id >= len(project_data["concepts"]):
        raise HTTPException(status_code=400, detail="Invalid concept selection")
    
    # 获取选定的概述
    selected_concept = project_data["concepts"][selection.concept_id]
    
    # 创建概述智能体
    narrative_agent = NarrativePathfinderAgent(llm=workflow.llm)
    
    # 调用智能体扩展概述
    result = await narrative_agent.run({
        "selected_concept": selected_concept,
        "mode": "expand"
    })
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "concept_expanded"
    projects[selection.request_id]["data"]["expanded_concept"] = result["expanded_concept"]
    
    return {
        "expanded_concept": result["expanded_concept"],
        "request_id": selection.request_id
    }

@router.post("/generate-world-settings", response_model=WorldSettingResponse)
async def generate_world_settings(
    selection: ConceptSelection,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """生成世界观设定"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    
    # 获取扩展后的概述或原始概述
    narrative_concept = project_data.get("expanded_concept", "")
    if not narrative_concept and "concepts" in project_data:
        if selection.concept_id < len(project_data["concepts"]):
            narrative_concept = project_data["concepts"][selection.concept_id]
    
    if not narrative_concept:
        raise HTTPException(status_code=400, detail="Narrative concept not found")
    
    # 创建世界观智能体
    world_agent = WorldWeaverAgent(llm=workflow.llm)
    
    # 调用智能体生成世界观
    result = await world_agent.run({
        "narrative_concept": narrative_concept,
        "num_settings": 3
    })
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "world_settings_generated"
    projects[selection.request_id]["data"]["world_settings"] = result["world_settings"]
    
    return {
        "world_settings": result["world_settings"],
        "request_id": selection.request_id
    }

@router.post("/select-world-setting", response_model=Dict[str, str])
async def select_world_setting(selection: WorldSettingSelection):
    """选择一个世界观设定"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    if "world_settings" not in project_data or selection.world_setting_id >= len(project_data["world_settings"]):
        raise HTTPException(status_code=400, detail="Invalid world setting selection")
    
    # 获取选定的世界观
    selected_world_setting = project_data["world_settings"][selection.world_setting_id]
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "world_setting_selected"
    projects[selection.request_id]["data"]["selected_world_setting"] = selected_world_setting
    
    return {"status": "success", "message": "World setting selected successfully"}

@router.post("/generate-plot-outlines", response_model=PlotOutlineResponse)
async def generate_plot_outlines(
    selection: WorldSettingSelection,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """生成小说大纲"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    
    # 获取扩展后的概述
    narrative_concept = project_data.get("expanded_concept", "")
    if not narrative_concept:
        raise HTTPException(status_code=400, detail="Expanded narrative concept not found")
    
    # 获取选定的世界观
    if "world_settings" not in project_data or selection.world_setting_id >= len(project_data["world_settings"]):
        raise HTTPException(status_code=400, detail="Invalid world setting selection")
    
    selected_world_setting = project_data["world_settings"][selection.world_setting_id]
    
    # 创建大纲智能体
    plot_agent = PlotArchitectAgent(llm=workflow.llm)
    
    # 调用智能体生成大纲
    result = await plot_agent.run({
        "narrative_concept": narrative_concept,
        "world_setting": selected_world_setting,
        "conflict_elements": ["主角内心冲突", "与反派的对抗", "环境挑战"],
        "chapter_count": 10,
        "num_outlines": 2
    })
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "plot_outlines_generated"
    projects[selection.request_id]["data"]["plot_outlines"] = result["plot_outlines"]
    
    return {
        "plot_outlines": result["plot_outlines"],
        "request_id": selection.request_id
    }

@router.post("/select-plot-outline", response_model=Dict[str, str])
async def select_plot_outline(selection: PlotOutlineSelection):
    """选择一个小说大纲"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    if "plot_outlines" not in project_data or selection.plot_outline_id >= len(project_data["plot_outlines"]):
        raise HTTPException(status_code=400, detail="Invalid plot outline selection")
    
    # 获取选定的大纲
    selected_plot_outline = project_data["plot_outlines"][selection.plot_outline_id]
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "plot_outline_selected"
    projects[selection.request_id]["data"]["selected_plot_outline"] = selected_plot_outline
    
    return {"status": "success", "message": "Plot outline selected successfully"}

@router.post("/generate-character-profiles", response_model=CharacterProfilesResponse)
async def generate_character_profiles(
    selection: PlotOutlineSelection,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """生成人物设定"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    
    # 获取扩展后的概述
    narrative_concept = project_data.get("expanded_concept", "")
    if not narrative_concept:
        raise HTTPException(status_code=400, detail="Expanded narrative concept not found")
    
    # 获取选定的世界观
    selected_world_setting = project_data.get("selected_world_setting", {})
    
    # 获取选定的大纲
    if "plot_outlines" not in project_data or selection.plot_outline_id >= len(project_data["plot_outlines"]):
        raise HTTPException(status_code=400, detail="Invalid plot outline selection")
    
    selected_plot_outline = project_data["plot_outlines"][selection.plot_outline_id]
    
    # 创建人物刻画智能体
    character_agent = CharacterSculptorAgent(llm=workflow.llm)
    
    # 调用智能体生成人物设定
    result = await character_agent.run({
        "narrative_concept": narrative_concept,
        "world_setting": selected_world_setting,
        "plot_outline": selected_plot_outline,
        "num_profiles": 2
    })
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "character_profiles_generated"
    projects[selection.request_id]["data"]["character_profiles"] = result["character_profiles"]
    
    return {
        "character_profiles": result["character_profiles"],
        "request_id": selection.request_id
    }

@router.post("/select-character-profiles", response_model=Dict[str, str])
async def select_character_profiles(selection: CharacterProfilesSelection):
    """选择一套人物设定"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[selection.request_id]["data"]
    if "character_profiles" not in project_data or selection.character_profiles_id >= len(project_data["character_profiles"]):
        raise HTTPException(status_code=400, detail="Invalid character profiles selection")
    
    # 获取选定的人物设定
    selected_character_profiles = project_data["character_profiles"][selection.character_profiles_id]
    
    # 更新项目状态
    projects[selection.request_id]["status"] = "character_profiles_selected"
    projects[selection.request_id]["data"]["selected_character_profiles"] = selected_character_profiles
    
    return {"status": "success", "message": "Character profiles selected successfully"}

@router.post("/generate-chapter", response_model=ChapterResponse)
async def generate_chapter(
    request: ChapterRequest,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """生成章节内容"""
    if request.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[request.request_id]["data"]
    
    # 获取选定的大纲
    selected_plot_outline = project_data.get("selected_plot_outline", {})
    if not selected_plot_outline:
        raise HTTPException(status_code=400, detail="Plot outline not selected")
    
    # 获取选定的世界观
    selected_world_setting = project_data.get("selected_world_setting", {})
    
    # 获取选定的人物设定
    selected_character_profiles = project_data.get("selected_character_profiles", [])
    
    # 获取章节大纲
    chapter_outline = {}
    if "章节列表" in selected_plot_outline:
        for chapter in selected_plot_outline["章节列表"]:
            if chapter["章节号"] == request.chapter_id:
                chapter_outline = chapter
                break
    
    if not chapter_outline:
        raise HTTPException(status_code=400, detail=f"Chapter {request.chapter_id} not found in plot outline")
    
    # 获取前情提要
    previous_summary = ""
    if request.chapter_id > 1 and "chapters" in project_data:
        # 创建总结智能体
        summary_agent = ContextSynthesizerAgent(llm=workflow.llm)
        
        # 获取已生成的章节
        chapters = []
        for i in range(1, request.chapter_id):
            if str(i) in project_data["chapters"]:
                chapters.append(project_data["chapters"][str(i)])
        
        # 调用智能体生成前情提要
        if chapters:
            summary_result = await summary_agent.run({
                "chapters": chapters,
                "key_events": [],
                "character_states": {},
                "mode": "quick"
            })
            previous_summary = summary_result["summary"]
    
    # 创建章节智能体
    chapter_agent = ChapterChroniclerAgent(llm=workflow.llm)
    
    # 调用智能体生成章节内容
    result = await chapter_agent.run({
        "chapter_outline": chapter_outline,
        "world_setting": selected_world_setting,
        "character_profiles": selected_character_profiles,
        "previous_summary": previous_summary,
        "kb_context": [],
        "writing_style": "流畅自然，细腻生动",
        "mode": "generate"
    })
    
    # 更新项目状态
    if "chapters" not in project_data:
        project_data["chapters"] = {}
    
    project_data["chapters"][str(request.chapter_id)] = {
        "chapter_number": request.chapter_id,
        "title": chapter_outline.get("标题", f"第{request.chapter_id}章"),
        "content": result["chapter_content"]
    }
    
    return {
        "chapter_content": result["chapter_content"],
        "chapter_id": request.chapter_id,
        "request_id": request.request_id
    }

@router.post("/generate-branches", response_model=BranchesResponse)
async def generate_branches(
    request: ChapterRequest,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """生成剧情分支"""
    if request.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[request.request_id]["data"]
    
    # 获取选定的大纲
    selected_plot_outline = project_data.get("selected_plot_outline", {})
    if not selected_plot_outline:
        raise HTTPException(status_code=400, detail="Plot outline not selected")
    
    # 获取选定的世界观
    selected_world_setting = project_data.get("selected_world_setting", {})
    
    # 获取选定的人物设定
    selected_character_profiles = project_data.get("selected_character_profiles", [])
    
    # 获取章节大纲
    chapter_outline = {}
    if "章节列表" in selected_plot_outline:
        for chapter in selected_plot_outline["章节列表"]:
            if chapter["章节号"] == request.chapter_id:
                chapter_outline = chapter
                break
    
    if not chapter_outline:
        raise HTTPException(status_code=400, detail=f"Chapter {request.chapter_id} not found in plot outline")
    
    # 获取前情提要
    previous_summary = ""
    if request.chapter_id > 1 and "chapters" in project_data:
        # 创建总结智能体
        summary_agent = ContextSynthesizerAgent(llm=workflow.llm)
        
        # 获取已生成的章节
        chapters = []
        for i in range(1, request.chapter_id):
            if str(i) in project_data["chapters"]:
                chapters.append(project_data["chapters"][str(i)])
        
        # 调用智能体生成前情提要
        if chapters:
            summary_result = await summary_agent.run({
                "chapters": chapters,
                "key_events": [],
                "character_states": {},
                "mode": "quick"
            })
            previous_summary = summary_result["summary"]
    
    # 创建章节智能体
    chapter_agent = ChapterChroniclerAgent(llm=workflow.llm)
    
    # 调用智能体生成剧情分支
    result = await chapter_agent.run({
        "chapter_outline": chapter_outline,
        "world_setting": selected_world_setting,
        "character_profiles": selected_character_profiles,
        "previous_summary": previous_summary,
        "kb_context": [],
        "branch_count": 3,
        "mode": "branches"
    })
    
    return {
        "plot_branches": result["plot_branches"],
        "chapter_id": request.chapter_id,
        "request_id": request.request_id
    }

@router.post("/select-branch", response_model=Dict[str, str])
async def select_branch(selection: BranchSelection):
    """选择一个剧情分支"""
    if selection.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # 这里应该更新大纲，但为了简化，我们只记录选择
    projects[selection.request_id]["data"]["selected_branch"] = {
        "branch_id": selection.branch_id,
        "chapter_id": selection.chapter_id
    }
    
    return {"status": "success", "message": "Branch selected successfully"}

@router.post("/evaluate-chapter", response_model=Dict[str, Any])
async def evaluate_chapter(
    request: ChapterRequest,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """评估章节内容"""
    if request.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[request.request_id]["data"]
    
    # 获取章节内容
    if "chapters" not in project_data or str(request.chapter_id) not in project_data["chapters"]:
        raise HTTPException(status_code=400, detail=f"Chapter {request.chapter_id} not found")
    
    chapter_content = project_data["chapters"][str(request.chapter_id)]["content"]
    
    # 获取选定的大纲
    selected_plot_outline = project_data.get("selected_plot_outline", {})
    
    # 获取章节大纲
    chapter_outline = {}
    if "章节列表" in selected_plot_outline:
        for chapter in selected_plot_outline["章节列表"]:
            if chapter["章节号"] == request.chapter_id:
                chapter_outline = chapter
                break
    
    # 获取选定的人物设定
    selected_character_profiles = project_data.get("selected_character_profiles", [])
    
    # 创建内容审核智能体
    content_agent = ContentIntegrityAgent(llm=workflow.llm)
    
    # 调用智能体评估章节内容
    result = await content_agent.run({
        "chapter_content": chapter_content,
        "chapter_outline": chapter_outline,
        "character_profiles": selected_character_profiles,
        "kb_snapshot": {},
        "writing_style": "流畅自然，细腻生动"
    })
    
    return result

@router.post("/polish-chapter", response_model=Dict[str, Any])
async def polish_chapter(
    request: ChapterRequest,
    workflow: NovelWorkflow = Depends(get_workflow)
):
    """润色章节内容"""
    if request.request_id not in projects:
        raise HTTPException(status_code=404, detail="Request not found")
    
    project_data = projects[request.request_id]["data"]
    
    # 获取章节内容
    if "chapters" not in project_data or str(request.chapter_id) not in project_data["chapters"]:
        raise HTTPException(status_code=400, detail=f"Chapter {request.chapter_id} not found")
    
    chapter_content = project_data["chapters"][str(request.chapter_id)]["content"]
    
    # 创建润色智能体
    style_agent = StylePolisherAgent(llm=workflow.llm)
    
    # 调用智能体润色章节内容
    result = await style_agent.run({
        "content": chapter_content,
        "style": "流畅自然，细腻生动",
        "focus_areas": ["描写", "对话", "情感"]
    })
    
    # 更新章节内容
    project_data["chapters"][str(request.chapter_id)]["content"] = result["polished_content"]
    
    return result

@router.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: str):
    """获取项目信息"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return projects[project_id]

@router.get("/projects/{project_id}/chapters", response_model=Dict[str, Any])
async def get_chapters(project_id: str):
    """获取项目的所有章节"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = projects[project_id]["data"]
    if "chapters" not in project_data:
        return {"chapters": {}}
    
    return {"chapters": project_data["chapters"]}

@router.get("/projects/{project_id}/chapters/{chapter_id}", response_model=Dict[str, Any])
async def get_chapter(project_id: str, chapter_id: str):
    """获取项目的特定章节"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = projects[project_id]["data"]
    if "chapters" not in project_data or chapter_id not in project_data["chapters"]:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter_id} not found")
    
    return project_data["chapters"][chapter_id]

@router.get("/projects/{project_id}/export", response_model=Dict[str, Any])
async def export_novel(project_id: str):
    """导出完整小说"""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = projects[project_id]["data"]
    if "chapters" not in project_data:
        raise HTTPException(status_code=400, detail="No chapters to export")
    
    # 获取选定的大纲
    selected_plot_outline = project_data.get("selected_plot_outline", {})
    
    # 构建完整小说
    novel = {
        "title": "自动生成的小说",  # 可以从项目数据中获取更好的标题
        "expanded_concept": project_data.get("expanded_concept", ""),
        "world_setting": project_data.get("selected_world_setting", {}),
        "plot_outline": selected_plot_outline,
        "character_profiles": project_data.get("selected_character_profiles", []),
        "chapters": []
    }
    
    # 按章节顺序添加章节
    chapter_ids = sorted([int(cid) for cid in project_data["chapters"].keys()])
    for cid in chapter_ids:
        chapter = project_data["chapters"][str(cid)]
        novel["chapters"].append({
            "chapter_number": chapter["chapter_number"],
            "title": chapter["title"],
            "content": chapter["content"]
        })
    
    return novel
