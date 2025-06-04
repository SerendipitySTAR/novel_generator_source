"""
项目数据模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Project(BaseModel):
    """项目模型"""
    __tablename__ = "projects"
    
    title = Column(String(255), nullable=False, comment="项目标题")
    description = Column(Text, comment="项目描述")
    status = Column(String(50), default="created", comment="项目状态")
    
    # 项目配置
    target_chapters = Column(Integer, default=10, comment="目标章节数")
    writing_style = Column(String(100), default="详细生动", comment="写作风格")
    genre = Column(String(100), comment="小说类型")
    
    # 项目元数据
    project_metadata = Column(JSON, default=dict, comment="项目元数据")
    
    # 关联关系
    concepts = relationship("Concept", back_populates="project", cascade="all, delete-orphan")
    world_settings = relationship("WorldSetting", back_populates="project", cascade="all, delete-orphan")
    plot_outlines = relationship("PlotOutline", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title})>"
