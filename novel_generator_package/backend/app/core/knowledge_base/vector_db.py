"""
向量数据库实现，基于ChromaDB
"""
import os
import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional, Any, Union
import uuid
import asyncio
from app.core.knowledge_base.kb_interface import KnowledgeBaseInterface
from app.core.llm import OpenAILLM
from app.config import settings

class VectorKnowledgeBase:
    """向量数据库实现类，负责RAG功能"""
    
    def __init__(self, collection_name: str = "novel_kb", persist_directory: Optional[str] = None):
        """
        初始化向量数据库
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录，如果为None则使用配置文件中的目录
        """
        self.persist_directory = persist_directory or settings.VECTOR_DB_PATH
        
        # 确保目录存在
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # 初始化ChromaDB客户端
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            chroma_db_impl="duckdb+parquet",
        ))
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # 初始化LLM用于生成嵌入向量
        self.llm = OpenAILLM()
    
    async def add_text_chunk(self, text: str, metadata: Dict[str, Any]) -> str:
        """
        添加文本块到向量数据库
        
        Args:
            text: 文本内容
            metadata: 元数据，包含文本来源、类型等信息
            
        Returns:
            str: 文本块ID
        """
        # 生成唯一ID
        chunk_id = str(uuid.uuid4())
        
        # 生成嵌入向量
        embeddings = await self.llm.generate_embeddings([text])
        
        # 添加到集合
        self.collection.add(
            ids=[chunk_id],
            embeddings=embeddings,
            metadatas=[metadata],
            documents=[text]
        )
        
        return chunk_id
    
    async def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索与查询相似的文本块
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 相似文本块列表，每个元素包含文本内容和元数据
        """
        # 生成查询文本的嵌入向量
        query_embedding = await self.llm.generate_embeddings([query])
        
        # 执行相似度搜索
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        # 格式化结果
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
        
        return formatted_results
