"""
概述相关API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Path
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from app.agents import NarrativePathfinderAgent
from app.core.llm import OpenAILLM

router = APIRouter()

# 概述存储（在实际应用中应该使用数据库）
concepts = {}

@router.post("", response_model=Dict[str, Any])
async def generate_concepts(
    project_id: str = Path(...),
    request: Dict[str, Any] = Body(...)
):
    """
    生成概述
    """
    user_input = request.get("user_input", "")
    num_concepts = request.get("num_concepts", 3)
    
    # 创建概述智能体
    agent = NarrativePathfinderAgent(llm=OpenAILLM(), project_id=project_id)
    
    # 生成概述
    result = await agent.run({
        "mode": "generate",
        "user_input": user_input,
        "num_concepts": num_concepts
    })
    
    # 保存概述
    project_concepts = []
    for i, concept_text in enumerate(result.get("concepts", [])):
        concept_id = str(uuid.uuid4())
        concept = {
            "id": concept_id,
            "project_id": project_id,
            "content": concept_text,
            "is_selected": False,
            "created_at": datetime.now().isoformat(),
            "expanded_content": None
        }
        
        if project_id not in concepts:
            concepts[project_id] = {}
        
        concepts[project_id][concept_id] = concept
        project_concepts.append(concept)
    
    return {
        "concepts": project_concepts
    }

@router.get("", response_model=List[Dict[str, Any]])
async def get_concepts(
    project_id: str = Path(...)
):
    """
    获取概述列表
    """
    if project_id not in concepts:
        return []
    
    return list(concepts[project_id].values())

@router.get("/{concept_id}", response_model=Dict[str, Any])
async def get_concept(
    project_id: str = Path(...),
    concept_id: str = Path(...)
):
    """
    获取概述详情
    """
    if project_id not in concepts or concept_id not in concepts[project_id]:
        raise HTTPException(status_code=404, detail="概述不存在")
    
    return concepts[project_id][concept_id]

@router.put("/{concept_id}", response_model=Dict[str, Any])
async def update_concept(
    project_id: str = Path(...),
    concept_id: str = Path(...),
    concept_update: Dict[str, Any] = Body(...)
):
    """
    更新概述
    """
    if project_id not in concepts or concept_id not in concepts[project_id]:
        raise HTTPException(status_code=404, detail="概述不存在")
    
    concept = concepts[project_id][concept_id]
    
    # 更新概述信息
    for key, value in concept_update.items():
        if key not in ["id", "project_id", "created_at"]:
            concept[key] = value
    
    # 如果将当前概述设为选中，则将其他概述设为未选中
    if concept_update.get("is_selected", False):
        for cid, c in concepts[project_id].items():
            if cid != concept_id:
                c["is_selected"] = False
    
    return concept

@router.post("/{concept_id}/expand", response_model=Dict[str, Any])
async def expand_concept(
    project_id: str = Path(...),
    concept_id: str = Path(...)
):
    """
    扩展概述为详细情节梗概
    """
    if project_id not in concepts or concept_id not in concepts[project_id]:
        raise HTTPException(status_code=404, detail="概述不存在")
    
    concept = concepts[project_id][concept_id]
    
    # 创建概述智能体
    agent = NarrativePathfinderAgent(llm=OpenAILLM(), project_id=project_id)
    
    # 扩展概述
    result = await agent.run({
        "mode": "expand",
        "selected_concept": concept["content"]
    })
    
    # 更新概述
    concept["expanded_content"] = result.get("expanded_content", "")
    
    return concept
