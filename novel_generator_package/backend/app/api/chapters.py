"""
章节相关API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.agents import ChapterChroniclerAgent
from app.agents.style_polisher import StylePolisherAgent
from app.core.llm import OpenAILLM

router = APIRouter()

# 章节存储（在实际应用中应该使用数据库）
chapters = {}

@router.post("", response_model=Dict[str, Any])
async def generate_chapter(
    project_id: str = Path(...),
    request: Dict[str, Any] = Body(...)
):
    """
    生成章节内容
    """
    chapter_outline = request.get("chapter_outline", {})
    world_setting = request.get("world_setting", {})
    character_profiles = request.get("character_profiles", [])
    previous_summary = request.get("previous_summary", "")
    kb_context = request.get("kb_context", [])
    writing_style = request.get("writing_style", "")
    selected_branch = request.get("selected_branch", {})
    
    # 创建章节智能体
    agent = ChapterChroniclerAgent(llm=OpenAILLM(), project_id=project_id)
    
    # 生成章节内容
    result = await agent.run({
        "mode": "generate",
        "chapter_outline": chapter_outline,
        "world_setting": world_setting,
        "character_profiles": character_profiles,
        "previous_summary": previous_summary,
        "kb_context": kb_context,
        "writing_style": writing_style,
        "selected_branch": selected_branch
    })

    # 添加调试日志
    print(f"章节生成结果: {result}")
    chapter_content = result.get("chapter_content", "")
    print(f"章节内容长度: {len(chapter_content)}")

    # 确保章节内容不为空
    if not chapter_content or chapter_content.strip() == "":
        chapter_content = "章节内容生成失败，请重试生成。如果问题持续存在，请检查AI服务配置。"
        print("警告: 章节内容为空，使用默认内容")

    # 保存章节
    chapter_id = str(uuid.uuid4())
    chapter = {
        "id": chapter_id,
        "project_id": project_id,
        "chapter_number": chapter_outline.get("number", 1),
        "title": chapter_outline.get("title", f"第{chapter_outline.get('number', 1)}章"),
        "content": chapter_content,
        "outline": chapter_outline,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    if project_id not in chapters:
        chapters[project_id] = {}
    
    chapters[project_id][chapter_id] = chapter
    
    return chapter

@router.post("/{chapter_id}/branches", response_model=Dict[str, Any])
async def generate_plot_branches(
    project_id: str = Path(...),
    chapter_id: str = Path(...),
    request: Dict[str, Any] = Body(...)
):
    """
    生成剧情分支
    """
    if project_id not in chapters or chapter_id not in chapters[project_id]:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    chapter = chapters[project_id][chapter_id]
    
    chapter_outline = chapter.get("outline", {})
    world_setting = request.get("world_setting", {})
    character_profiles = request.get("character_profiles", [])
    previous_summary = request.get("previous_summary", "")
    kb_context = request.get("kb_context", [])
    
    # 创建章节智能体
    agent = ChapterChroniclerAgent(llm=OpenAILLM(), project_id=project_id)
    
    # 生成剧情分支
    result = await agent.run({
        "mode": "branches",
        "chapter_outline": chapter_outline,
        "world_setting": world_setting,
        "character_profiles": character_profiles,
        "previous_summary": previous_summary,
        "kb_context": kb_context
    })
    
    return {
        "plot_branches": result.get("plot_branches", [])
    }

@router.get("", response_model=List[Dict[str, Any]])
async def get_chapters(
    project_id: str = Path(...)
):
    """
    获取章节列表
    """
    if project_id not in chapters:
        return []
    
    return list(chapters[project_id].values())

@router.get("/{chapter_id}", response_model=Dict[str, Any])
async def get_chapter(
    project_id: str = Path(...),
    chapter_id: str = Path(...)
):
    """
    获取章节详情
    """
    if project_id not in chapters or chapter_id not in chapters[project_id]:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    return chapters[project_id][chapter_id]

@router.put("/{chapter_id}", response_model=Dict[str, Any])
async def update_chapter(
    project_id: str = Path(...),
    chapter_id: str = Path(...),
    chapter_update: Dict[str, Any] = Body(...)
):
    """
    更新章节
    """
    if project_id not in chapters or chapter_id not in chapters[project_id]:
        raise HTTPException(status_code=404, detail="章节不存在")
    
    chapter = chapters[project_id][chapter_id]
    
    # 更新章节信息
    for key, value in chapter_update.items():
        if key not in ["id", "project_id", "created_at"]:
            chapter[key] = value
    
    chapter["updated_at"] = datetime.now().isoformat()
    
    return chapter

@router.post("/{chapter_id}/polish", response_model=Dict[str, Any])
async def polish_chapter(
    project_id: str = Path(...),
    chapter_id: str = Path(...),
    request: Dict[str, Any] = Body(...)
):
    """
    润色章节
    """
    if project_id not in chapters or chapter_id not in chapters[project_id]:
        raise HTTPException(status_code=404, detail="章节不存在")

    chapter = chapters[project_id][chapter_id]
    style = request.get("style", "详细生动")
    focus_areas = request.get("focus_areas", ["描写", "对话", "情感"])

    # 创建润色智能体
    agent = StylePolisherAgent(llm=OpenAILLM(), project_id=project_id)

    # 润色章节内容
    result = await agent.run({
        "content": chapter.get("content", ""),
        "style": style,
        "focus_areas": focus_areas
    })

    # 更新章节内容
    chapter["content"] = result.get("polished_content", chapter.get("content", ""))
    chapter["polish_summary"] = result.get("changes_summary", "")
    chapter["updated_at"] = datetime.now().isoformat()

    return chapter
