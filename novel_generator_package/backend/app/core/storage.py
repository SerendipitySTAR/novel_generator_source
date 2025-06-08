"""
统一数据存储服务
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.core.exceptions import ResourceNotFoundError, DatabaseError, handle_exceptions
from app.db.repositories import (
    ProjectRepository, ConceptRepository, WorldSettingRepository,
    PlotOutlineRepository, CharacterRepository, ChapterRepository
)

logger = get_logger("novel_generator.storage")


class StorageService:
    """统一数据存储服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.concept_repo = ConceptRepository(db)
        self.world_setting_repo = WorldSettingRepository(db)
        self.plot_outline_repo = PlotOutlineRepository(db)
        self.character_repo = CharacterRepository(db)
        self.chapter_repo = ChapterRepository(db)
        
        logger.debug("StorageService initialized")
    
    # 项目相关操作
    @handle_exceptions("Failed to create project")
    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目"""
        logger.info("Creating new project", title=project_data.get("title"))

        project = self.project_repo.create(**project_data)
        self.db.commit()

        logger.info("Project created successfully", project_id=project.id)
        return project.to_dict()
    
    @handle_exceptions("Failed to get project")
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """获取项目"""
        logger.debug("Getting project", project_id=project_id)
        
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project", project_id)
        
        return project.to_dict()
    
    @handle_exceptions("Failed to update project")
    def update_project(self, project_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新项目"""
        logger.info("Updating project", project_id=project_id)
        
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project", project_id)
        
        updated_project = self.project_repo.update(project_id, **update_data)
        self.db.commit()
        
        logger.info("Project updated successfully", project_id=project_id)
        return updated_project.to_dict()
    
    @handle_exceptions("Failed to delete project")
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        logger.info("Deleting project", project_id=project_id)
        
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError("Project", project_id)
        
        self.project_repo.delete(project)
        self.db.commit()
        
        logger.info("Project deleted successfully", project_id=project_id)
        return True
    
    @handle_exceptions("Failed to list projects")
    def list_projects(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取项目列表"""
        logger.debug("Listing projects", limit=limit, offset=offset)

        projects = self.project_repo.get_all(skip=offset, limit=limit)
        return [project.to_dict() for project in projects]
    
    # 概述相关操作
    @handle_exceptions("Failed to create concept")
    def create_concept(self, project_id: str, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建概述"""
        logger.info("Creating concept", project_id=project_id)
        
        # 验证项目存在
        if not self.project_repo.get_by_id(project_id):
            raise ResourceNotFoundError("Project", project_id)
        
        concept_data["project_id"] = project_id
        concept = self.concept_repo.create(**concept_data)
        self.db.commit()
        
        logger.info("Concept created successfully", concept_id=concept.id)
        return concept.to_dict()
    
    @handle_exceptions("Failed to get concepts")
    def get_concepts(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的概述列表"""
        logger.debug("Getting concepts", project_id=project_id)
        
        concepts = self.concept_repo.get_by_project_id(project_id)
        return [concept.to_dict() for concept in concepts]
    
    @handle_exceptions("Failed to update concept")
    def update_concept(self, concept_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新概述"""
        logger.info("Updating concept", concept_id=concept_id)

        concept = self.concept_repo.get_by_id(concept_id)
        if not concept:
            raise ResourceNotFoundError("Concept", concept_id)

        updated_concept = self.concept_repo.update(concept_id, **update_data)
        self.db.commit()

        logger.info("Concept updated successfully", concept_id=concept_id)
        return updated_concept.to_dict()
    
    # 世界观设定相关操作
    @handle_exceptions("Failed to create world setting")
    def create_world_setting(self, project_id: str, world_setting_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建世界观设定"""
        logger.info("Creating world setting", project_id=project_id)
        
        # 验证项目存在
        if not self.project_repo.get_by_id(project_id):
            raise ResourceNotFoundError("Project", project_id)
        
        world_setting_data["project_id"] = project_id
        world_setting = self.world_setting_repo.create(**world_setting_data)
        self.db.commit()
        
        logger.info("World setting created successfully", world_setting_id=world_setting.id)
        return world_setting.to_dict()
    
    @handle_exceptions("Failed to get world settings")
    def get_world_settings(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的世界观设定列表"""
        logger.debug("Getting world settings", project_id=project_id)
        
        world_settings = self.world_setting_repo.get_by_project_id(project_id)
        return [ws.to_dict() for ws in world_settings]
    
    # 大纲相关操作
    @handle_exceptions("Failed to create plot outline")
    def create_plot_outline(self, project_id: str, plot_outline_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建大纲"""
        logger.info("Creating plot outline", project_id=project_id)
        
        # 验证项目存在
        if not self.project_repo.get_by_id(project_id):
            raise ResourceNotFoundError("Project", project_id)
        
        plot_outline_data["project_id"] = project_id
        plot_outline = self.plot_outline_repo.create(**plot_outline_data)
        self.db.commit()
        
        logger.info("Plot outline created successfully", plot_outline_id=plot_outline.id)
        return plot_outline.to_dict()
    
    @handle_exceptions("Failed to get plot outlines")
    def get_plot_outlines(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的大纲列表"""
        logger.debug("Getting plot outlines", project_id=project_id)
        
        plot_outlines = self.plot_outline_repo.get_by_project_id(project_id)
        return [po.to_dict() for po in plot_outlines]
    
    # 人物设定相关操作
    @handle_exceptions("Failed to create character")
    def create_character(self, project_id: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建人物设定"""
        logger.info("Creating character", project_id=project_id)
        
        # 验证项目存在
        if not self.project_repo.get_by_id(project_id):
            raise ResourceNotFoundError("Project", project_id)
        
        character_data["project_id"] = project_id
        character = self.character_repo.create(**character_data)
        self.db.commit()
        
        logger.info("Character created successfully", character_id=character.id)
        return character.to_dict()
    
    @handle_exceptions("Failed to get characters")
    def get_characters(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的人物设定列表"""
        logger.debug("Getting characters", project_id=project_id)
        
        characters = self.character_repo.get_by_project_id(project_id)
        return [char.to_dict() for char in characters]
    
    # 章节相关操作
    @handle_exceptions("Failed to create chapter")
    def create_chapter(self, project_id: str, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建章节"""
        logger.info("Creating chapter", project_id=project_id, chapter_number=chapter_data.get("chapter_number"))
        
        # 验证项目存在
        if not self.project_repo.get_by_id(project_id):
            raise ResourceNotFoundError("Project", project_id)
        
        chapter_data["project_id"] = project_id
        chapter = self.chapter_repo.create(**chapter_data)
        self.db.commit()
        
        logger.info("Chapter created successfully", chapter_id=chapter.id)
        return chapter.to_dict()
    
    @handle_exceptions("Failed to get chapters")
    def get_chapters(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的章节列表"""
        logger.debug("Getting chapters", project_id=project_id)
        
        chapters = self.chapter_repo.get_by_project_id(project_id)
        return [chapter.to_dict() for chapter in chapters]
    
    @handle_exceptions("Failed to update chapter")
    def update_chapter(self, chapter_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新章节"""
        logger.info("Updating chapter", chapter_id=chapter_id)
        
        chapter = self.chapter_repo.get_by_id(chapter_id)
        if not chapter:
            raise ResourceNotFoundError("Chapter", chapter_id)
        
        updated_chapter = self.chapter_repo.update(chapter_id, **update_data)
        self.db.commit()
        
        logger.info("Chapter updated successfully", chapter_id=chapter_id)
        return updated_chapter.to_dict()
    
    # 批量操作
    @handle_exceptions("Failed to get project summary")
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """获取项目摘要信息"""
        logger.debug("Getting project summary", project_id=project_id)
        
        project = self.get_project(project_id)
        
        # 获取各类内容的统计信息
        concepts = self.get_concepts(project_id)
        world_settings = self.get_world_settings(project_id)
        plot_outlines = self.get_plot_outlines(project_id)
        characters = self.get_characters(project_id)
        chapters = self.get_chapters(project_id)
        
        # 计算进度
        progress = self._calculate_progress(
            concepts, world_settings, plot_outlines, characters, chapters
        )
        
        summary = {
            "project": project,
            "stats": {
                "concepts_count": len(concepts),
                "world_settings_count": len(world_settings),
                "plot_outlines_count": len(plot_outlines),
                "characters_count": len(characters),
                "chapters_count": len(chapters)
            },
            "progress": progress
        }
        
        logger.debug("Project summary generated", project_id=project_id, progress=progress)
        return summary
    
    def _calculate_progress(self, concepts, world_settings, plot_outlines, characters, chapters) -> int:
        """计算项目进度"""
        total_steps = 5  # 概述、世界观、大纲、人物、章节
        completed_steps = 0
        
        if concepts:
            completed_steps += 1
        if world_settings:
            completed_steps += 1
        if plot_outlines:
            completed_steps += 1
        if characters:
            completed_steps += 1
        if chapters:
            completed_steps += 1
        
        return int((completed_steps / total_steps) * 100)
