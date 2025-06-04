"""
世界观设定数据模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class WorldSetting(BaseModel):
    """世界观设定模型"""
    __tablename__ = "world_settings"
    
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), comment="世界观标题")
    content = Column(JSON, nullable=False, comment="世界观设定内容")
    
    # 状态字段
    is_selected = Column(Boolean, default=False, comment="是否被选中")
    order_index = Column(Integer, comment="排序索引")
    
    # 评估结果
    quality_score = Column(Integer, comment="质量评分")
    evaluation_result = Column(JSON, comment="评估结果详情")
    
    # 关联关系
    project = relationship("Project", back_populates="world_settings")
    
    def __repr__(self):
        return f"<WorldSetting(id={self.id}, title={self.title})>"
