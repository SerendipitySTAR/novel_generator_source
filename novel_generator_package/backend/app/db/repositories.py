"""
数据访问层 - Repository模式
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.models import (
    Project, Concept, WorldSetting, 
    PlotOutline, Character, Chapter
)

class BaseRepository:
    """基础Repository类"""
    
    def __init__(self, db: Session, model_class):
        self.db = db
        self.model_class = model_class
    
    def create(self, **kwargs) -> Any:
        """创建记录"""
        obj = self.model_class(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def get_by_id(self, id: str) -> Optional[Any]:
        """根据ID获取记录"""
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Any]:
        """获取所有记录"""
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, id: str, **kwargs) -> Optional[Any]:
        """更新记录"""
        obj = self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj
    
    def delete(self, id: str) -> bool:
        """删除记录"""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

class ProjectRepository(BaseRepository):
    """项目Repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, Project)
    
    def get_by_title(self, title: str) -> Optional[Project]:
        """根据标题获取项目"""
        return self.db.query(Project).filter(Project.title == title).first()
    
    def get_recent_projects(self, limit: int = 10) -> List[Project]:
        """获取最近的项目"""
        return self.db.query(Project).order_by(desc(Project.updated_at)).limit(limit).all()

class ConceptRepository(BaseRepository):
    """概述Repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, Concept)
    
    def get_by_project_id(self, project_id: str) -> List[Concept]:
        """根据项目ID获取概述列表"""
        return self.db.query(Concept).filter(
            Concept.project_id == project_id
        ).order_by(asc(Concept.order_index)).all()
    
    def get_selected_by_project_id(self, project_id: str) -> Optional[Concept]:
        """获取项目选中的概述"""
        return self.db.query(Concept).filter(
            Concept.project_id == project_id,
            Concept.is_selected == True
        ).first()
    
    def set_selected(self, project_id: str, concept_id: str) -> bool:
        """设置选中的概述"""
        # 先取消所有选中状态
        self.db.query(Concept).filter(
            Concept.project_id == project_id
        ).update({"is_selected": False})
        
        # 设置新的选中状态
        concept = self.get_by_id(concept_id)
        if concept and concept.project_id == project_id:
            concept.is_selected = True
            self.db.commit()
            return True
        return False

class WorldSettingRepository(BaseRepository):
    """世界观设定Repository"""
    
    def __init__(self, db: Session):
        super().__init__(db, WorldSetting)
    
    def get_by_project_id(self, project_id: str) -> List[WorldSetting]:
        """根据项目ID获取世界观设定列表"""
        return self.db.query(WorldSetting).filter(
            WorldSetting.project_id == project_id
        ).order_by(asc(WorldSetting.order_index)).all()
    
    def get_selected_by_project_id(self, project_id: str) -> Optional[WorldSetting]:
        """获取项目选中的世界观设定"""
        return self.db.query(WorldSetting).filter(
            WorldSetting.project_id == project_id,
            WorldSetting.is_selected == True
        ).first()
    
    def set_selected(self, project_id: str, world_setting_id: str) -> bool:
        """设置选中的世界观设定"""
        # 先取消所有选中状态
        self.db.query(WorldSetting).filter(
            WorldSetting.project_id == project_id
        ).update({"is_selected": False})
        
        # 设置新的选中状态
        world_setting = self.get_by_id(world_setting_id)
        if world_setting and world_setting.project_id == project_id:
            world_setting.is_selected = True
            self.db.commit()
            return True
        return False

class PlotOutlineRepository(BaseRepository):
    """大纲Repository"""

    def __init__(self, db: Session):
        super().__init__(db, PlotOutline)

    def get_by_project_id(self, project_id: str) -> List[PlotOutline]:
        """根据项目ID获取大纲列表"""
        return self.db.query(PlotOutline).filter(
            PlotOutline.project_id == project_id
        ).order_by(asc(PlotOutline.order_index)).all()

    def get_selected_by_project_id(self, project_id: str) -> Optional[PlotOutline]:
        """获取项目选中的大纲"""
        return self.db.query(PlotOutline).filter(
            PlotOutline.project_id == project_id,
            PlotOutline.is_selected == True
        ).first()

    def set_selected(self, project_id: str, plot_outline_id: str) -> bool:
        """设置选中的大纲"""
        # 先取消所有选中状态
        self.db.query(PlotOutline).filter(
            PlotOutline.project_id == project_id
        ).update({"is_selected": False})

        # 设置新的选中状态
        plot_outline = self.get_by_id(plot_outline_id)
        if plot_outline and plot_outline.project_id == project_id:
            plot_outline.is_selected = True
            self.db.commit()
            return True
        return False

class CharacterRepository(BaseRepository):
    """人物设定Repository"""

    def __init__(self, db: Session):
        super().__init__(db, Character)

    def get_by_project_id(self, project_id: str) -> List[Character]:
        """根据项目ID获取人物设定列表"""
        return self.db.query(Character).filter(
            Character.project_id == project_id
        ).order_by(asc(Character.order_index)).all()

    def get_selected_by_project_id(self, project_id: str) -> List[Character]:
        """获取项目选中的人物设定"""
        return self.db.query(Character).filter(
            Character.project_id == project_id,
            Character.is_selected == True
        ).all()

    def set_selected(self, project_id: str, character_id: str) -> bool:
        """设置选中的人物设定"""
        # 先取消所有选中状态
        self.db.query(Character).filter(
            Character.project_id == project_id
        ).update({"is_selected": False})

        # 设置新的选中状态
        character = self.get_by_id(character_id)
        if character and character.project_id == project_id:
            character.is_selected = True
            self.db.commit()
            return True
        return False

class ChapterRepository(BaseRepository):
    """章节Repository"""

    def __init__(self, db: Session):
        super().__init__(db, Chapter)

    def get_by_project_id(self, project_id: str) -> List[Chapter]:
        """根据项目ID获取章节列表"""
        return self.db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).order_by(asc(Chapter.chapter_number)).all()

    def get_by_chapter_number(self, project_id: str, chapter_number: int) -> Optional[Chapter]:
        """根据章节号获取章节"""
        return self.db.query(Chapter).filter(
            Chapter.project_id == project_id,
            Chapter.chapter_number == chapter_number
        ).first()

    def get_latest_chapter(self, project_id: str) -> Optional[Chapter]:
        """获取最新章节"""
        return self.db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).order_by(desc(Chapter.chapter_number)).first()

    def count_by_project_id(self, project_id: str) -> int:
        """统计项目章节数"""
        return self.db.query(Chapter).filter(
            Chapter.project_id == project_id
        ).count()
