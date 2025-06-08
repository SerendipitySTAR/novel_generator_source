"""
项目服务层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models import Project, Concept, WorldSetting, PlotOutline, Character, Chapter
from app.db.repositories import (
    ProjectRepository, ConceptRepository, WorldSettingRepository,
    PlotOutlineRepository, CharacterRepository, ChapterRepository
)

class ProjectService:
    """项目服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.concept_repo = ConceptRepository(db)
        self.world_setting_repo = WorldSettingRepository(db)
        self.plot_outline_repo = PlotOutlineRepository(db)
        self.character_repo = CharacterRepository(db)
        self.chapter_repo = ChapterRepository(db)
    
    def create_project(self, title: str, description: str = "", **kwargs) -> Project:
        """创建新项目"""
        return self.project_repo.create(
            title=title,
            description=description,
            **kwargs
        )
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """获取项目详情"""
        return self.project_repo.get_by_id(project_id)
    
    def get_all_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """获取所有项目"""
        return self.project_repo.get_all(skip=skip, limit=limit)
    
    def get_recent_projects(self, limit: int = 10) -> List[Project]:
        """获取最近的项目"""
        return self.project_repo.get_recent_projects(limit=limit)
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Project]:
        """更新项目"""
        return self.project_repo.update(project_id, **kwargs)
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        return self.project_repo.delete(project_id)
    
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """获取项目摘要信息"""
        project = self.get_project(project_id)
        if not project:
            return {}
        
        # 获取各类内容的统计信息
        concepts = self.concept_repo.get_by_project_id(project_id)
        world_settings = self.world_setting_repo.get_by_project_id(project_id)
        plot_outlines = self.plot_outline_repo.get_by_project_id(project_id)
        characters = self.character_repo.get_by_project_id(project_id)
        chapters = self.chapter_repo.get_by_project_id(project_id)
        
        # 计算进度
        progress = self._calculate_progress(
            concepts, world_settings, plot_outlines, characters, chapters
        )
        
        # 获取选中的项目
        selected_concept = self.concept_repo.get_selected_by_project_id(project_id)
        selected_world_setting = self.world_setting_repo.get_selected_by_project_id(project_id)
        selected_plot_outline = self.plot_outline_repo.get_selected_by_project_id(project_id)
        selected_characters = self.character_repo.get_selected_by_project_id(project_id)

        return {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at if isinstance(project.created_at, str) else (project.created_at.isoformat() if project.created_at else None),
            "updated_at": project.updated_at if isinstance(project.updated_at, str) else (project.updated_at.isoformat() if project.updated_at else None),
            "stats": {
                "concepts_count": len(concepts),
                "world_settings_count": len(world_settings),
                "plot_outlines_count": len(plot_outlines),
                "characters_count": len(characters),
                "chapters_count": len(chapters),
                "progress_percentage": progress
            },
            "selected_items": {
                "concept": selected_concept.to_dict() if selected_concept else None,
                "world_setting": selected_world_setting.to_dict() if selected_world_setting else None,
                "plot_outline": selected_plot_outline.to_dict() if selected_plot_outline else None,
                "characters": [c.to_dict() for c in selected_characters] if selected_characters else []
            }
        }
    
    def _calculate_progress(self, concepts, world_settings, plot_outlines, characters, chapters) -> int:
        """计算项目进度百分比"""
        total_steps = 5  # 概述、世界观、大纲、人物、章节
        completed_steps = 0
        
        # 检查是否有选中的概述
        if any(c.is_selected for c in concepts):
            completed_steps += 1
        
        # 检查是否有选中的世界观设定
        if any(w.is_selected for w in world_settings):
            completed_steps += 1
        
        # 检查是否有选中的大纲
        if any(p.is_selected for p in plot_outlines):
            completed_steps += 1
        
        # 检查是否有选中的人物设定
        if any(c.is_selected for c in characters):
            completed_steps += 1
        
        # 检查是否有章节
        if chapters:
            completed_steps += 1
        
        return int((completed_steps / total_steps) * 100)
