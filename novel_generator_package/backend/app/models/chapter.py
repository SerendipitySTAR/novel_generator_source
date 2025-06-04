"""
章节数据模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Chapter(BaseModel):
    """章节模型"""
    __tablename__ = "chapters"
    
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False, comment="章节号")
    title = Column(String(255), comment="章节标题")
    content = Column(Text, comment="章节内容")
    outline = Column(JSON, comment="章节大纲")
    
    # 状态字段
    status = Column(String(50), default="draft", comment="章节状态：draft/completed/reviewed")
    word_count = Column(Integer, default=0, comment="字数统计")
    
    # 评估结果
    quality_score = Column(Integer, comment="质量评分")
    evaluation_result = Column(JSON, comment="评估结果详情")
    
    # 生成相关
    writing_style = Column(String(100), comment="写作风格")
    generation_metadata = Column(JSON, comment="生成元数据")
    
    # 关联关系
    project = relationship("Project", back_populates="chapters")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, chapter_number={self.chapter_number}, title={self.title})>"
