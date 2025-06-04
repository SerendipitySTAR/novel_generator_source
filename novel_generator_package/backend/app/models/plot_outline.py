"""
大纲数据模型
"""
from sqlalchemy import Column, String, Text, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class PlotOutline(BaseModel):
    """大纲模型"""
    __tablename__ = "plot_outlines"
    
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), comment="大纲标题")
    content = Column(JSON, nullable=False, comment="大纲内容")
    
    # 状态字段
    is_selected = Column(Boolean, default=False, comment="是否被选中")
    order_index = Column(Integer, comment="排序索引")
    
    # 评估结果
    quality_score = Column(Integer, comment="质量评分")
    evaluation_result = Column(JSON, comment="评估结果详情")
    
    # 关联关系
    project = relationship("Project", back_populates="plot_outlines")
    
    def __repr__(self):
        return f"<PlotOutline(id={self.id}, title={self.title})>"
