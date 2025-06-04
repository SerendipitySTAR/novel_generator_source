"""
知识库接口定义，提供统一的知识存储和检索接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union

class KnowledgeBaseInterface(ABC):
    """知识库接口抽象类"""
    
    @abstractmethod
    async def add_text_chunk(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        添加文本块到知识库
        
        Args:
            text: 文本内容
            metadata: 元数据，包含文本来源、类型等信息
            
        Returns:
            str: 文本块ID
        """
        pass
    
    @abstractmethod
    async def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索与查询相似的文本块
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 相似文本块列表，每个元素包含文本内容和元数据
        """
        pass
    
    @abstractmethod
    async def add_entity(self, entity_type: str, properties: Dict[str, Any]) -> str:
        """
        添加实体到知识库
        
        Args:
            entity_type: 实体类型，如Character, Location等
            properties: 实体属性
            
        Returns:
            str: 实体ID
        """
        pass
    
    @abstractmethod
    async def add_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        relationship_type: str, 
        properties: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        添加实体间关系
        
        Args:
            source_id: 源实体ID
            target_id: 目标实体ID
            relationship_type: 关系类型
            properties: 关系属性
            
        Returns:
            str: 关系ID
        """
        pass
    
    @abstractmethod
    async def query_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        查询实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            Dict[str, Any]: 实体信息
        """
        pass
    
    @abstractmethod
    async def query_relationships(
        self, 
        entity_id: str, 
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        查询实体的关系
        
        Args:
            entity_id: 实体ID
            relationship_type: 关系类型，如果为None则查询所有关系
            
        Returns:
            List[Dict[str, Any]]: 关系列表
        """
        pass
    
    @abstractmethod
    async def detect_conflicts(self, extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检测信息冲突
        
        Args:
            extracted_info: 提取的信息
            
        Returns:
            List[Dict[str, Any]]: 冲突列表
        """
        pass
