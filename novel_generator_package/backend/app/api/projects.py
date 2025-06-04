"""
项目相关API路由
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

router = APIRouter()

# 项目存储（在实际应用中应该使用数据库）
projects = {}

@router.post("", response_model=Dict[str, Any])
async def create_project(
    project: Dict[str, Any] = Body(...)
):
    """
    创建新项目
    """
    project_id = str(uuid.uuid4())
    project["id"] = project_id
    project["created_at"] = datetime.now().isoformat()
    project["updated_at"] = project["created_at"]
    project["status"] = "draft"
    
    projects[project_id] = project
    
    return project

@router.get("", response_model=List[Dict[str, Any]])
async def get_projects():
    """
    获取项目列表
    """
    return list(projects.values())

@router.get("/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: str):
    """
    获取项目详情
    """
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return projects[project_id]

@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(
    project_id: str,
    project_update: Dict[str, Any] = Body(...)
):
    """
    更新项目
    """
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    project = projects[project_id]
    
    # 更新项目信息
    for key, value in project_update.items():
        if key not in ["id", "created_at"]:
            project[key] = value
    
    project["updated_at"] = datetime.now().isoformat()
    
    return project

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    删除项目
    """
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    del projects[project_id]
    
    return {"message": "项目已删除"}
