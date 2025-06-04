"""
OpenAI LLM实现，提供对OpenAI API的调用（支持本地vLLM服务器）
"""
from openai import AsyncOpenAI
import tiktoken
from typing import Dict, List, Optional, Any, Union
import asyncio
from sentence_transformers import SentenceTransformer
from app.core.llm.llm_interface import LLMInterface, LLMResponse
from app.config import settings

class OpenAILLM(LLMInterface):
    """OpenAI LLM实现类"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        初始化OpenAI LLM（支持本地vLLM服务器）

        Args:
            api_key: OpenAI API密钥，如果为None则使用配置文件中的密钥
            model: 默认使用的模型，如果为None则使用配置文件中的模型
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.DEFAULT_LLM_MODEL
        self.embedding_model_path = settings.DEFAULT_EMBEDDING_MODEL

        # 初始化AsyncOpenAI客户端（支持本地vLLM服务器）
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=settings.OPENAI_API_BASE
        )

        # 初始化本地embedding模型
        self.embedding_model = None
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_path)
            print(f"成功加载本地embedding模型: {self.embedding_model_path}")
        except Exception as e:
            print(f"加载本地embedding模型失败: {e}")
            print("将使用OpenAI embedding API作为备选")
    
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
        使用OpenAI API生成文本
        
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
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stop=stop,
                **kwargs
            )

            # 安全地处理usage数据，过滤掉None值
            usage_dict = response.usage.model_dump()
            safe_usage = {}
            for key, value in usage_dict.items():
                if value is not None and isinstance(value, (int, float)):
                    safe_usage[key] = int(value)
                elif key in ['prompt_tokens', 'completion_tokens', 'total_tokens']:
                    # 为必需的字段提供默认值
                    safe_usage[key] = 0

            return LLMResponse(
                text=response.choices[0].message.content,
                model=response.model,
                usage=safe_usage,
                finish_reason=response.choices[0].finish_reason,
                metadata={"id": response.id}
            )
        except Exception as e:
            # 在实际应用中应该有更好的错误处理
            print(f"OpenAI API调用失败: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        生成文本嵌入向量（优先使用本地模型）

        Args:
            texts: 文本列表

        Returns:
            List[List[float]]: 嵌入向量列表
        """
        # 优先使用本地embedding模型
        if self.embedding_model is not None:
            try:
                embeddings = self.embedding_model.encode(texts)
                return embeddings.tolist()
            except Exception as e:
                print(f"本地embedding模型调用失败: {str(e)}")
                print("尝试使用OpenAI embedding API作为备选")

        # 备选：使用OpenAI embedding API
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",  # 使用默认的OpenAI embedding模型
                input=texts
            )

            # 提取嵌入向量
            embeddings = [item.embedding for item in response.data]
            return embeddings
        except Exception as e:
            print(f"OpenAI Embedding API调用失败: {str(e)}")
            raise
    
    async def count_tokens(self, text: str) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: token数量
        """
        try:
            # 根据模型选择合适的编码器
            if "gpt-4" in self.model:
                encoding = tiktoken.encoding_for_model("gpt-4")
            elif "gpt-3.5-turbo" in self.model:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            else:
                encoding = tiktoken.get_encoding("cl100k_base")
            
            # 计算token数量
            tokens = encoding.encode(text)
            return len(tokens)
        except Exception as e:
            print(f"Token计算失败: {str(e)}")
            # 如果失败，使用简单的估算方法
            return len(text) // 4
