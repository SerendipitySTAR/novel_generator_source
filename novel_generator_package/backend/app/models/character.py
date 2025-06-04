"""
人物设定数据模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Character(BaseModel):
    """人物设定模型"""
    __tablename__ = "characters"
    
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), comment="人物姓名")
    content = Column(JSON, nullable=False, comment="人物设定内容")
    
    # 状态字段
    is_selected = Column(Boolean, default=False, comment="是否被选中")
    order_index = Column(Integer, comment="排序索引")
    character_type = Column(String(50), default="main", comment="人物类型：main/supporting/minor")
    
    # 评估结果
    quality_score = Column(Integer, comment="质量评分")
    evaluation_result = Column(JSON, comment="评估结果详情")
    
    # 关联关系
    project = relationship("Project", back_populates="characters")
    
    def __repr__(self):
        return f"<Character(id={self.id}, name={self.name})>"
