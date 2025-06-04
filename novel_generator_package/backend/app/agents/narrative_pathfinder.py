"""
概述智能体 (Narrative Pathfinder Agent)
负责根据用户输入生成核心创意概述和详细情节梗概
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.core.llm import LLMInterface, LLMResponse
from app.core.knowledge_base import KnowledgeBase
from app.config import settings

class NarrativePathfinderAgent(BaseAgent):
    """概述智能体，负责生成小说核心创意概述和详细情节梗概"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行概述智能体
        
        Args:
            input_data: 输入数据，包含:
                - user_input: 用户输入的初始信息
                - num_concepts: 需要生成的概述数量
                - mode: 'generate' 生成核心创意概述 或 'expand' 扩展为详细情节梗概
                - selected_concept: (仅在mode='expand'时需要) 用户选定的核心创意概述
                
        Returns:
            Dict[str, Any]: 输出数据，包含:
                - concepts: 生成的核心创意概述列表 (mode='generate')
                - expanded_concept: 扩展后的详细情节梗概 (mode='expand')
        """
        mode = input_data.get("mode", "generate")
        
        if mode == "generate":
            return await self._generate_concepts(input_data)
        elif mode == "expand":
            return await self._expand_concept(input_data)
        else:
            raise ValueError(f"不支持的模式: {mode}")
    
    async def _generate_concepts(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成多个核心创意概述
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        user_input = input_data.get("user_input", "")
        num_concepts = input_data.get("num_concepts", 3)
        
        # 构建提示词
        prompt_template = """
        你是一位富有创意的小说策划师。根据以下用户输入，请构思{num_concepts}个不同但都引人入胜的小说的核心创意概述（500-1000字）。
        
        每个概述需包含：
        1. 核心概念
        2. 主要冲突
        3. 主要角色类型
        4. 故事亮点
        5. 预期风格和主题
        
        请确保每个概述都有独特的吸引力，并且具有发展为长篇小说的潜力。
        
        用户输入:
        {user_input}
        
        请按照以下格式输出，为每个概述添加编号:
        
        ## 概述1
        [第一个概述内容]
        
        ## 概述2
        [第二个概述内容]
        
        ...以此类推
        """
        
        prompt = await self._generate_prompt(prompt_template, {
            "num_concepts": num_concepts,
            "user_input": user_input
        })
        
        # 调用LLM生成概述
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=settings.CONCEPT_MAX_TOKENS,
            top_p=0.9
        )
        
        # 解析响应，提取概述
        concepts = self._parse_concepts(response.text, num_concepts)

        return {
            "concepts": concepts
        }
    
    async def _expand_concept(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        将选定的核心创意概述扩展为详细情节梗概
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        selected_concept = input_data.get("selected_concept", "")
        
        # 构建提示词
        prompt_template = """
        基于以下已选定的核心创意概述，请将其扩展为一个更详细的情节梗概（约3000字），细化主要事件顺序、关键转折和结局方向。
        
        请包含以下内容:
        1. 故事背景的更多细节
        2. 主要角色的初步描述和动机
        3. 故事的开端、发展、高潮和结局
        4. 主要情节线和可能的次要情节线
        5. 关键冲突的具体表现和解决方向
        6. 主题的深化和探索
        
        已选定的核心创意概述:
        {selected_concept}
        
        请提供一个连贯、有深度且引人入胜的情节梗概，为后续的世界观构建和大纲创作奠定基础。
        """
        
        prompt = await self._generate_prompt(prompt_template, {
            "selected_concept": selected_concept
        })
        
        # 调用LLM扩展概述
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=settings.CONCEPT_EXPAND_MAX_TOKENS,
            top_p=0.9
        )
        
        return {
            "expanded_concept": response.text
        }
    
    def _parse_concepts(self, text: str, num_concepts: int = 3) -> List[str]:
        """
        从LLM响应中解析出概述列表

        Args:
            text: LLM响应文本
            num_concepts: 需要的概述数量

        Returns:
            List[str]: 概述列表
        """
        concepts = []

        # 尝试多种分隔符模式
        patterns = [
            "## 概述",
            "### 概述",
            "**概述",
            "概述",
            "##",
            "###"
        ]

        for pattern in patterns:
            sections = text.split(pattern)
            if len(sections) > 1:
                # 跳过第一个空部分（如果存在）
                for i, section in enumerate(sections[1:], 1):
                    concept = section.strip()
                    if concept:
                        # 清理概述内容，移除数字前缀
                        concept = self._clean_concept_text(concept)
                        if concept and len(concept) > 50:  # 确保概述有足够的内容
                            concepts.append(concept)
                break

        # 如果上面的方法没有找到概述，尝试按数字分割
        if not concepts:
            for i in range(1, 10):
                for separator in [f"{i}.", f"{i}、", f"第{i}个", f"概述{i}"]:
                    sections = text.split(separator)
                    if len(sections) > 1:
                        for section in sections[1:]:
                            concept = section.strip()
                            if concept:
                                concept = self._clean_concept_text(concept)
                                if concept and len(concept) > 50:
                                    concepts.append(concept)
                        if concepts:
                            break
                if concepts:
                    break

        # 如果仍然没有找到概述，将整个文本作为一个概述
        if not concepts:
            cleaned_text = self._clean_concept_text(text)
            if cleaned_text:
                concepts = [cleaned_text]

        # 去重并限制数量
        unique_concepts = []
        for concept in concepts:
            if concept not in unique_concepts:
                unique_concepts.append(concept)
            # 达到指定数量就停止
            if len(unique_concepts) >= num_concepts:
                break

        return unique_concepts[:num_concepts]

    def _clean_concept_text(self, text: str) -> str:
        """
        清理概述文本，移除不必要的前缀和格式

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本
        """
        # 移除数字前缀
        import re
        text = re.sub(r'^\d+[.、：:]?\s*', '', text.strip())

        # 移除常见的标题前缀
        prefixes_to_remove = [
            "概述", "小说概述", "故事概述", "核心创意",
            "创意概述", "情节概述", "故事梗概"
        ]

        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                # 移除可能的分隔符
                text = re.sub(r'^[：:：\-\s]+', '', text)

        return text.strip()
