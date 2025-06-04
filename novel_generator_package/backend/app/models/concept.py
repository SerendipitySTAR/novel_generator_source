"""
概述数据模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Concept(BaseModel):
    """概述模型"""
    __tablename__ = "concepts"
    
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), comment="概述标题")
    content = Column(Text, nullable=False, comment="概述内容")
    expanded_content = Column(Text, comment="扩展后的详细情节梗概")
    
    # 状态字段
    is_selected = Column(Boolean, default=False, comment="是否被选中")
    order_index = Column(Integer, comment="排序索引")
    
    # 评估结果
    quality_score = Column(Integer, comment="质量评分")
    evaluation_result = Column(JSON, comment="评估结果详情")
    
    # 关联关系
    project = relationship("Project", back_populates="concepts")
    
    def __repr__(self):
        return f"<Concept(id={self.id}, title={self.title})>"
