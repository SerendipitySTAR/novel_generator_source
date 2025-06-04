"""
知识库实现，整合向量数据库和知识图谱
"""
from typing import Dict, List, Optional, Any, Union
import uuid
import asyncio
from app.core.knowledge_base.kb_interface import KnowledgeBaseInterface
from app.core.knowledge_base.vector_db import VectorKnowledgeBase
from app.config import settings

class KnowledgeBase(KnowledgeBaseInterface):
    """知识库实现类，整合向量数据库和知识图谱"""
    
    def __init__(self, project_id: str):
        """
        初始化知识库
        
        Args:
            project_id: 项目ID，用于区分不同项目的知识库
        """
        self.project_id = project_id
        self.vector_db = VectorKnowledgeBase(collection_name=f"novel_kb_{project_id}")
        # 知识图谱暂未实现，将在后续版本中添加
        self.graph_db = None
        
        # 内存中存储实体和关系，用于简化实现
        # 在实际应用中，应该使用Neo4j等图数据库
        self.entities = {}
        self.relationships = []
    
    async def add_text_chunk(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        添加文本块到知识库
        
        Args:
            text: 文本内容
            metadata: 元数据，包含文本来源、类型等信息
            
        Returns:
            str: 文本块ID
        """
        # 添加项目ID到元数据
        metadata["project_id"] = self.project_id
        
        # 添加到向量数据库
        return await self.vector_db.add_text_chunk(text, metadata)
    
    async def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索与查询相似的文本块
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 相似文本块列表，每个元素包含文本内容和元数据
        """
        return await self.vector_db.search_similar_chunks(query, top_k)
    
    async def add_entity(self, entity_type: str, properties: Dict[str, Any]) -> str:
        """
        添加实体到知识库
        
        Args:
            entity_type: 实体类型，如Character, Location等
            properties: 实体属性
            
        Returns:
            str: 实体ID
        """
        # 生成唯一ID
        entity_id = str(uuid.uuid4())
        
        # 添加项目ID和实体类型
        properties["project_id"] = self.project_id
        properties["entity_type"] = entity_type
        
        # 存储实体
        self.entities[entity_id] = properties
        
        # 同时添加到向量数据库，便于语义搜索
        # 构建实体描述文本
        entity_text = f"类型: {entity_type}\n"
        for key, value in properties.items():
            if key not in ["project_id", "entity_type"]:
                entity_text += f"{key}: {value}\n"
        
        await self.vector_db.add_text_chunk(
            entity_text, 
            {
                "id": entity_id,
                "type": "entity",
                "entity_type": entity_type,
                "project_id": self.project_id
            }
        )
        
        return entity_id
    
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
        # 生成唯一ID
        relationship_id = str(uuid.uuid4())
        
        # 创建关系对象
        relationship = {
            "id": relationship_id,
            "source_id": source_id,
            "target_id": target_id,
            "type": relationship_type,
            "properties": properties or {},
            "project_id": self.project_id
        }
        
        # 存储关系
        self.relationships.append(relationship)
        
        # 同时添加到向量数据库，便于语义搜索
        # 构建关系描述文本
        source_entity = self.entities.get(source_id, {})
        target_entity = self.entities.get(target_id, {})
        
        source_name = source_entity.get("name", source_id)
        target_name = target_entity.get("name", target_id)
        
        relationship_text = f"关系: {source_name} {relationship_type} {target_name}\n"
        if properties:
            for key, value in properties.items():
                relationship_text += f"{key}: {value}\n"
        
        await self.vector_db.add_text_chunk(
            relationship_text, 
            {
                "id": relationship_id,
                "type": "relationship",
                "relationship_type": relationship_type,
                "source_id": source_id,
                "target_id": target_id,
                "project_id": self.project_id
            }
        )
        
        return relationship_id
    
    async def query_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        查询实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            Dict[str, Any]: 实体信息
        """
        return self.entities.get(entity_id, {})
    
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
        results = []
        
        for rel in self.relationships:
            if (rel["source_id"] == entity_id or rel["target_id"] == entity_id) and \
               (relationship_type is None or rel["type"] == relationship_type):
                results.append(rel)
        
        return results
    
    async def detect_conflicts(self, extracted_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检测信息冲突
        
        Args:
            extracted_info: 提取的信息
            
        Returns:
            List[Dict[str, Any]]: 冲突列表
        """
        conflicts = []
        
        # 简单实现，仅检查实体属性冲突
        if "entity_updates" in extracted_info:
            for entity_update in extracted_info["entity_updates"]:
                entity_id = entity_update.get("id")
                if entity_id and entity_id in self.entities:
                    existing_entity = self.entities[entity_id]
                    for key, new_value in entity_update.get("properties", {}).items():
                        if key in existing_entity and existing_entity[key] != new_value:
                            conflicts.append({
                                "type": "entity_property_conflict",
                                "entity_id": entity_id,
                                "property": key,
                                "existing_value": existing_entity[key],
                                "new_value": new_value
                            })
        
        return conflicts
