"""
总结智能体，负责生成不同粒度的前情提要
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class ContextSynthesizerAgent(BaseAgent):
    """总结智能体"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行总结智能体
        
        Args:
            input_data: 输入数据，包含：
                - chapters: 已生成的全部章节或其摘要
                - key_events: 知识库中的关键事件列表
                - character_states: 人物状态
                - mode: 模式，"detailed"表示生成详细提要，"quick"表示生成快速回顾摘要
            
        Returns:
            Dict[str, Any]: 输出数据，包含：
                - summary: 生成的前情提要
        """
        chapters = input_data.get("chapters", [])
        key_events = input_data.get("key_events", [])
        character_states = input_data.get("character_states", {})
        mode = input_data.get("mode", "detailed")
        
        if mode == "detailed":
            return await self._generate_detailed_summary(input_data)
        elif mode == "quick":
            return await self._generate_quick_recap(input_data)
        else:
            raise ValueError(f"不支持的模式: {mode}")
    
    async def _generate_detailed_summary(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成详细提要
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        chapters = input_data.get("chapters", [])
        key_events = input_data.get("key_events", [])
        character_states = input_data.get("character_states", {})
        
        # 构建提示词
        prompt_template = """你是一位精炼的叙事总结者。根据以下已有的故事内容、关键事件和人物状态，为即将开始的新章节，生成一份详细的前情提要。提要应包含故事至今核心脉络、上一章详细事件和结局、当前主要人物精确状态和直接面临的挑战、与即将发生剧情最相关的知识库条目。请高亮显示以下关键信息：人物目标、未解的悬念、重要的伏笔。

已有的故事内容:
{chapters_text}

关键事件:
{key_events_text}

人物状态:
{character_states_text}

请生成一份详细的前情提要，确保包含以下内容：
1. 故事核心脉络概述
2. 上一章详细事件和结局
3. 当前主要人物状态和面临的挑战
4. 未解的悬念和伏笔

请使用**加粗**来高亮显示关键信息。
"""
        
        # 将章节内容转换为文本
        chapters_text = self._chapters_to_text(chapters)
        
        # 将关键事件转换为文本
        key_events_text = self._key_events_to_text(key_events)
        
        # 将人物状态转换为文本
        character_states_text = self._character_states_to_text(character_states)
        
        prompt = await self._generate_prompt(prompt_template, {
            "chapters_text": chapters_text,
            "key_events_text": key_events_text,
            "character_states_text": character_states_text
        })
        
        # 调用LLM生成详细提要
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.5,
            max_tokens=settings.AGENT_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )
        
        return {"summary": response.text}
    
    async def _generate_quick_recap(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成快速回顾摘要
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        chapters = input_data.get("chapters", [])
        key_events = input_data.get("key_events", [])
        
        # 构建提示词
        prompt_template = """你是一位精炼的叙事总结者。根据以下已有的故事内容和关键事件，为读者生成一份简洁的快速回顾摘要。摘要应突出主线情节，帮助读者快速回忆故事发展。

已有的故事内容:
{chapters_text}

关键事件:
{key_events_text}

请生成一份简洁的快速回顾摘要，确保包含以下内容：
1. 故事主线概述
2. 关键转折点
3. 主要人物当前状态

请控制在500字以内，使用**加粗**来高亮显示关键信息。
"""
        
        # 将章节内容转换为文本
        chapters_text = self._chapters_to_text(chapters)
        
        # 将关键事件转换为文本
        key_events_text = self._key_events_to_text(key_events)
        
        prompt = await self._generate_prompt(prompt_template, {
            "chapters_text": chapters_text,
            "key_events_text": key_events_text
        })
        
        # 调用LLM生成快速回顾摘要
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.5,
            max_tokens=1000,  # 快速回顾摘要应该更短
            top_p=settings.AGENT_TOP_P
        )
        
        return {"summary": response.text}
    
    def _chapters_to_text(self, chapters: List[Dict[str, Any]]) -> str:
        """
        将章节内容转换为文本
        
        Args:
            chapters: 章节内容
            
        Returns:
            str: 文本形式的章节内容
        """
        text = ""
        
        for i, chapter in enumerate(chapters):
            if isinstance(chapter, str):
                # 如果章节是字符串，直接添加
                text += f"第{i+1}章:\n{chapter}\n\n"
            elif isinstance(chapter, dict):
                # 如果章节是字典，提取内容
                chapter_number = chapter.get("chapter_number", i+1)
                title = chapter.get("title", "无标题")
                content = chapter.get("content", "")
                
                text += f"第{chapter_number}章: {title}\n{content}\n\n"
        
        return text
    
    def _key_events_to_text(self, key_events: List[Dict[str, Any]]) -> str:
        """
        将关键事件转换为文本
        
        Args:
            key_events: 关键事件列表
            
        Returns:
            str: 文本形式的关键事件
        """
        text = ""
        
        for event in key_events:
            if isinstance(event, str):
                # 如果事件是字符串，直接添加
                text += f"- {event}\n"
            elif isinstance(event, dict):
                # 如果事件是字典，提取描述
                description = event.get("description", "")
                chapter = event.get("chapter", "")
                
                if chapter:
                    text += f"- [{chapter}] {description}\n"
                else:
                    text += f"- {description}\n"
        
        return text
    
    def _character_states_to_text(self, character_states: Dict[str, Any]) -> str:
        """
        将人物状态转换为文本
        
        Args:
            character_states: 人物状态
            
        Returns:
            str: 文本形式的人物状态
        """
        text = ""
        
        for name, state in character_states.items():
            text += f"【{name}】\n"
            
            if isinstance(state, str):
                # 如果状态是字符串，直接添加
                text += f"{state}\n"
            elif isinstance(state, dict):
                # 如果状态是字典，提取信息
                location = state.get("location", "")
                if location:
                    text += f"位置: {location}\n"
                
                health = state.get("health", "")
                if health:
                    text += f"状态: {health}\n"
                
                items = state.get("items", [])
                if items:
                    text += f"持有物: {', '.join(items)}\n"
                
                emotion = state.get("emotion", "")
                if emotion:
                    text += f"情绪: {emotion}\n"
                
                goal = state.get("goal", "")
                if goal:
                    text += f"目标: {goal}\n"
            
            text += "\n"
        
        return text
