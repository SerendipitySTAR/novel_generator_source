"""
大语言模型抽象层，提供统一的LLM调用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel

class LLMResponse(BaseModel):
    """LLM响应的标准格式"""
    text: str
    model: str
    usage: Dict[str, int]
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class LLMInterface(ABC):
    """大语言模型接口抽象类"""
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        temperature: float = 0.7, 
        max_tokens: int = 1000,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成文本
        
        Args:
            prompt: 提示词
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            top_p: 核采样参数
            stop: 停止生成的标记
            **kwargs: 其他参数
            
        Returns:
            LLMResponse: 包含生成文本和元数据的响应对象
        """
        pass
    
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        生成文本嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: token数量
        """
        pass
