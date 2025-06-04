"""
知识库层初始化文件
"""
from app.core.knowledge_base.kb_interface import KnowledgeBaseInterface
from app.core.knowledge_base.vector_db import VectorKnowledgeBase
from app.core.knowledge_base.knowledge_base import KnowledgeBase

__all__ = ["KnowledgeBaseInterface", "VectorKnowledgeBase", "KnowledgeBase"]
