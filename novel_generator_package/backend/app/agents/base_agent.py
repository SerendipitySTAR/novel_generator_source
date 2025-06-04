"""
智能体基类，定义所有智能体的通用接口和方法
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from app.core.llm import LLMInterface, OpenAILLM
from app.core.knowledge_base import KnowledgeBase
from app.config import settings

class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(
        self, 
        llm: Optional[LLMInterface] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        project_id: Optional[str] = None
    ):
        """
        初始化智能体
        
        Args:
            llm: 大语言模型接口
            knowledge_base: 知识库
            project_id: 项目ID
        """
        self.llm = llm or OpenAILLM()
        self.project_id = project_id
        self.knowledge_base = knowledge_base
        
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行智能体
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        pass
    
    async def _generate_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """
        生成提示词
        
        Args:
            template: 提示词模板
            variables: 变量
            
        Returns:
            str: 生成的提示词
        """
        # 简单的模板替换
        prompt = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        return prompt
