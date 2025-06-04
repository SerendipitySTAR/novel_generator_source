"""
世界观设定相关API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.agents import WorldWeaverAgent
from app.core.llm import OpenAILLM

router = APIRouter()

# 世界观设定存储（在实际应用中应该使用数据库）
world_settings = {}

@router.post("", response_model=Dict[str, Any])
async def generate_world_settings(
    project_id: str = Path(...),
    request: Dict[str, Any] = Body(...)
):
    """
    生成世界观设定
    """
    narrative_concept = request.get("narrative_concept", "")
    num_settings = request.get("num_settings", 3)
    
    # 创建世界观智能体
    agent = WorldWeaverAgent(llm=OpenAILLM(), project_id=project_id)
    
    # 生成世界观设定
    result = await agent.run({
        "narrative_concept": narrative_concept,
        "num_settings": num_settings
    })
    
    # 保存世界观设定
    project_settings = []
    for i, setting in enumerate(result.get("world_settings", [])):
        setting_id = str(uuid.uuid4())
        world_setting = {
            "id": setting_id,
            "project_id": project_id,
            "content": setting,
            "is_selected": False,
            "created_at": datetime.now().isoformat()
        }
        
        if project_id not in world_settings:
            world_settings[project_id] = {}
        
        world_settings[project_id][setting_id] = world_setting
        project_settings.append(world_setting)
    
    return {
        "world_settings": project_settings
    }

@router.get("", response_model=List[Dict[str, Any]])
async def get_world_settings(
    project_id: str = Path(...)
):
    """
    获取世界观设定列表
    """
    if project_id not in world_settings:
        return []
    
    return list(world_settings[project_id].values())

@router.get("/{setting_id}", response_model=Dict[str, Any])
async def get_world_setting(
    project_id: str = Path(...),
    setting_id: str = Path(...)
):
    """
    获取世界观设定详情
    """
    if project_id not in world_settings or setting_id not in world_settings[project_id]:
        raise HTTPException(status_code=404, detail="世界观设定不存在")
    
    return world_settings[project_id][setting_id]

@router.put("/{setting_id}", response_model=Dict[str, Any])
async def update_world_setting(
    project_id: str = Path(...),
    setting_id: str = Path(...),
    setting_update: Dict[str, Any] = Body(...)
):
    """
    更新世界观设定
    """
    if project_id not in world_settings or setting_id not in world_settings[project_id]:
        raise HTTPException(status_code=404, detail="世界观设定不存在")
    
    setting = world_settings[project_id][setting_id]
    
    # 更新世界观设定信息
    for key, value in setting_update.items():
        if key not in ["id", "project_id", "created_at"]:
            setting[key] = value
    
    # 如果将当前世界观设定设为选中，则将其他世界观设定设为未选中
    if setting_update.get("is_selected", False):
        for sid, s in world_settings[project_id].items():
            if sid != setting_id:
                s["is_selected"] = False
    
    return setting
