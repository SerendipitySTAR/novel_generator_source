"""
大纲相关API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.agents import PlotArchitectAgent
from app.core.llm import OpenAILLM

router = APIRouter()

# 大纲存储（在实际应用中应该使用数据库）
plot_outlines = {}

@router.post("", response_model=Dict[str, Any])
async def generate_plot_outlines(
    project_id: str = Path(...),
    request: Dict[str, Any] = Body(...)
):
    """
    生成大纲
    """
    narrative_concept = request.get("narrative_concept", "")
    world_setting = request.get("world_setting", {})
    conflict_elements = request.get("conflict_elements", [])
    chapter_count = request.get("chapter_count", 10)
    num_outlines = request.get("num_outlines", 1)
    
    # 创建大纲智能体
    agent = PlotArchitectAgent(llm=OpenAILLM(), project_id=project_id)
    
    # 生成大纲
    result = await agent.run({
        "narrative_concept": narrative_concept,
        "world_setting": world_setting,
        "conflict_elements": conflict_elements,
        "chapter_count": chapter_count,
        "num_outlines": num_outlines
    })
    
    # 保存大纲
    project_outlines = []
    for i, outline in enumerate(result.get("plot_outlines", [])):
        outline_id = str(uuid.uuid4())
        plot_outline = {
            "id": outline_id,
            "project_id": project_id,
            "content": outline,
            "is_selected": False,
            "created_at": datetime.now().isoformat()
        }
        
        if project_id not in plot_outlines:
            plot_outlines[project_id] = {}
        
        plot_outlines[project_id][outline_id] = plot_outline
        project_outlines.append(plot_outline)
    
    return {
        "plot_outlines": project_outlines
    }

@router.get("", response_model=List[Dict[str, Any]])
async def get_plot_outlines(
    project_id: str = Path(...)
):
    """
    获取大纲列表
    """
    if project_id not in plot_outlines:
        return []
    
    return list(plot_outlines[project_id].values())

@router.get("/{outline_id}", response_model=Dict[str, Any])
async def get_plot_outline(
    project_id: str = Path(...),
    outline_id: str = Path(...)
):
    """
    获取大纲详情
    """
    if project_id not in plot_outlines or outline_id not in plot_outlines[project_id]:
        raise HTTPException(status_code=404, detail="大纲不存在")
    
    return plot_outlines[project_id][outline_id]

@router.put("/{outline_id}", response_model=Dict[str, Any])
async def update_plot_outline(
    project_id: str = Path(...),
    outline_id: str = Path(...),
    outline_update: Dict[str, Any] = Body(...)
):
    """
    更新大纲
    """
    if project_id not in plot_outlines or outline_id not in plot_outlines[project_id]:
        raise HTTPException(status_code=404, detail="大纲不存在")
    
    outline = plot_outlines[project_id][outline_id]
    
    # 更新大纲信息
    for key, value in outline_update.items():
        if key not in ["id", "project_id", "created_at"]:
            outline[key] = value
    
    # 如果将当前大纲设为选中，则将其他大纲设为未选中
    if outline_update.get("is_selected", False):
        for oid, o in plot_outlines[project_id].items():
            if oid != outline_id:
                o["is_selected"] = False
    
    return outline
