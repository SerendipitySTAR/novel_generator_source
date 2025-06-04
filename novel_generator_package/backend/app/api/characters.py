"""
人物相关API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.agents import CharacterSculptorAgent
from app.core.llm import OpenAILLM

router = APIRouter()

# 人物设定存储（在实际应用中应该使用数据库）
characters = {}

@router.post("", response_model=Dict[str, Any])
async def generate_characters(
    project_id: str = Path(...),
    request: Dict[str, Any] = Body(...)
):
    """
    生成人物设定
    """
    narrative_concept = request.get("narrative_concept", "")
    world_setting = request.get("world_setting", {})
    plot_outline = request.get("plot_outline", {})
    num_profiles = request.get("num_profiles", 1)
    
    # 创建人物刻画智能体
    agent = CharacterSculptorAgent(llm=OpenAILLM(), project_id=project_id)
    
    # 生成人物设定
    result = await agent.run({
        "narrative_concept": narrative_concept,
        "world_setting": world_setting,
        "plot_outline": plot_outline,
        "num_profiles": num_profiles
    })
    
    # 保存人物设定
    project_characters = []
    for i, profile_set in enumerate(result.get("character_profiles", [])):
        profile_id = str(uuid.uuid4())
        character_profile = {
            "id": profile_id,
            "project_id": project_id,
            "content": profile_set,
            "is_selected": False,
            "created_at": datetime.now().isoformat()
        }
        
        if project_id not in characters:
            characters[project_id] = {}
        
        characters[project_id][profile_id] = character_profile
        project_characters.append(character_profile)
    
    return {
        "characters": project_characters
    }

@router.get("", response_model=List[Dict[str, Any]])
async def get_characters(
    project_id: str = Path(...)
):
    """
    获取人物设定列表
    """
    if project_id not in characters:
        return []
    
    return list(characters[project_id].values())

@router.get("/{character_id}", response_model=Dict[str, Any])
async def get_character(
    project_id: str = Path(...),
    character_id: str = Path(...)
):
    """
    获取人物设定详情
    """
    if project_id not in characters or character_id not in characters[project_id]:
        raise HTTPException(status_code=404, detail="人物设定不存在")
    
    return characters[project_id][character_id]

@router.put("/{character_id}", response_model=Dict[str, Any])
async def update_character(
    project_id: str = Path(...),
    character_id: str = Path(...),
    character_update: Dict[str, Any] = Body(...)
):
    """
    更新人物设定
    """
    if project_id not in characters or character_id not in characters[project_id]:
        raise HTTPException(status_code=404, detail="人物设定不存在")
    
    character = characters[project_id][character_id]
    
    # 更新人物设定信息
    for key, value in character_update.items():
        if key not in ["id", "project_id", "created_at"]:
            character[key] = value
    
    # 如果将当前人物设定设为选中，则将其他人物设定设为未选中
    if character_update.get("is_selected", False):
        for cid, c in characters[project_id].items():
            if cid != character_id:
                c["is_selected"] = False
    
    return character
