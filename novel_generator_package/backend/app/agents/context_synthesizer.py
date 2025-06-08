"""
总结智能体，负责生成不同粒度的前情提要
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class ContextSynthesizerAgent(BaseAgent):
    """总结智能体 - 增强版本，支持分层上下文管理"""

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行总结智能体

        Args:
            input_data: 输入数据，包含：
                - chapters: 已生成的全部章节或其摘要
                - key_events: 知识库中的关键事件列表
                - character_states: 人物状态
                - world_setting: 世界观设定
                - character_profiles: 人物设定
                - mode: 模式，"detailed"表示生成详细提要，"quick"表示生成快速回顾摘要，"layered"表示分层上下文

        Returns:
            Dict[str, Any]: 输出数据，包含：
                - summary: 生成的前情提要
                - global_context: 全局上下文（世界观、主要人物）
                - medium_context: 中期上下文（近期章节的关键事件）
                - immediate_context: 即时上下文（上一章的直接影响）
        """
        chapters = input_data.get("chapters", [])
        key_events = input_data.get("key_events", [])
        character_states = input_data.get("character_states", {})
        world_setting = input_data.get("world_setting", {})
        character_profiles = input_data.get("character_profiles", [])
        mode = input_data.get("mode", "detailed")

        if mode == "detailed":
            return await self._generate_detailed_summary(input_data)
        elif mode == "quick":
            return await self._generate_quick_recap(input_data)
        elif mode == "layered":
            return await self._generate_layered_context(chapters, world_setting, character_profiles, key_events, character_states)
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

    async def _generate_layered_context(self, chapters: List[Dict], world_setting: Dict, character_profiles: List[Dict], key_events: List, character_states: Dict) -> Dict[str, Any]:
        """
        生成分层上下文管理

        Args:
            chapters: 章节列表
            world_setting: 世界观设定
            character_profiles: 人物设定
            key_events: 关键事件
            character_states: 人物状态

        Returns:
            Dict[str, Any]: 分层上下文结果
        """
        # 1. 全局上下文（世界观、主要人物）
        global_context = await self._build_global_context(world_setting, character_profiles)

        # 2. 中期上下文（近期章节的关键事件）
        medium_context = await self._build_medium_context(chapters, key_events)

        # 3. 即时上下文（上一章的直接影响）
        immediate_context = await self._build_immediate_context(chapters)

        # 4. 综合前情提要
        comprehensive_summary = await self._build_comprehensive_summary(global_context, medium_context, immediate_context)

        return {
            "summary": comprehensive_summary,
            "global_context": global_context,
            "medium_context": medium_context,
            "immediate_context": immediate_context
        }

    async def _build_global_context(self, world_setting: Dict, character_profiles: List[Dict]) -> str:
        """
        构建全局上下文（世界观、主要人物）
        """
        prompt_template = """请根据以下世界观设定和人物设定，生成一个简洁的全局背景介绍（200字以内）：

## 世界观设定：
{world_setting_text}

## 主要人物：
{character_profiles_text}

请提取最核心的世界观要素和主要人物信息，形成简洁的背景介绍。重点突出：
1. 世界的基本设定和特色
2. 主要人物的身份和关系
3. 核心的世界规则或体系

格式要求：简洁明了，突出重点，控制在200字以内。
"""

        world_setting_text = self._world_setting_to_text(world_setting)
        character_profiles_text = self._character_profiles_to_text(character_profiles)

        prompt = await self._generate_prompt(prompt_template, {
            "world_setting_text": world_setting_text[:500],  # 限制长度
            "character_profiles_text": character_profiles_text[:500]
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=300,
            top_p=settings.AGENT_TOP_P
        )

        return response.text.strip()

    async def _build_medium_context(self, chapters: List[Dict], key_events: List) -> str:
        """
        构建中期上下文（近期章节的关键事件）
        """
        if not chapters:
            return "这是故事的开始。"

        # 取最近3-5章
        recent_chapters = chapters[-5:] if len(chapters) > 5 else chapters

        prompt_template = """请根据以下近期章节内容，提取关键事件和重要发展（300字以内）：

## 近期章节：
{recent_chapters_text}

## 已知关键事件：
{key_events_text}

请重点关注：
1. 重要的情节发展和转折点
2. 人物关系的变化
3. 新出现的冲突或问题
4. 对后续发展有影响的事件

格式要求：按时间顺序，突出关键事件，控制在300字以内。
"""

        recent_chapters_text = ""
        for chapter in recent_chapters:
            title = chapter.get("title", f"第{chapter.get('chapter_number', '')}章")
            content = chapter.get("content", "")
            # 提取章节摘要
            summary = content[:150] + "..." if len(content) > 150 else content
            recent_chapters_text += f"{title}：{summary}\n\n"

        key_events_text = self._key_events_to_text(key_events)

        prompt = await self._generate_prompt(prompt_template, {
            "recent_chapters_text": recent_chapters_text,
            "key_events_text": key_events_text[:300]
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.4,
            max_tokens=400,
            top_p=settings.AGENT_TOP_P
        )

        return response.text.strip()

    async def _build_immediate_context(self, chapters: List[Dict]) -> str:
        """
        构建即时上下文（上一章的直接影响）
        """
        if not chapters:
            return "故事即将开始。"

        last_chapter = chapters[-1]

        prompt_template = """请根据上一章的内容，总结对下一章的直接影响（150字以内）：

## 上一章内容：
标题：{last_chapter_title}
内容：{last_chapter_content}

请重点关注：
1. 章节结尾的情况和悬念
2. 人物当前的状态和位置
3. 未解决的问题或冲突
4. 对下一章的直接影响

格式要求：简洁明了，重点突出，控制在150字以内。
"""

        last_chapter_title = last_chapter.get("title", f"第{last_chapter.get('chapter_number', '')}章")
        last_chapter_content = last_chapter.get("content", "")

        prompt = await self._generate_prompt(prompt_template, {
            "last_chapter_title": last_chapter_title,
            "last_chapter_content": last_chapter_content[:800]  # 限制长度
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=200,
            top_p=settings.AGENT_TOP_P
        )

        return response.text.strip()

    async def _build_comprehensive_summary(self, global_context: str, medium_context: str, immediate_context: str) -> str:
        """
        构建综合前情提要
        """
        prompt_template = """请根据以下分层信息，生成一个完整的前情提要（500字以内）：

## 全局背景：
{global_context}

## 近期发展：
{medium_context}

## 当前状况：
{immediate_context}

请整合以上信息，生成一个连贯、完整的前情提要。要求：
1. 逻辑清晰，层次分明
2. 突出重点，避免冗余
3. 为下一章的生成提供充分的背景信息
4. 控制在500字以内

格式：使用**加粗**突出关键信息。
"""

        prompt = await self._generate_prompt(prompt_template, {
            "global_context": global_context,
            "medium_context": medium_context,
            "immediate_context": immediate_context
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.4,
            max_tokens=600,
            top_p=settings.AGENT_TOP_P
        )

        return response.text.strip()

    def _world_setting_to_text(self, world_setting: Dict) -> str:
        """
        将世界观设定转换为文本（简化版）
        """
        if not world_setting:
            return "暂无世界观设定。"

        text = ""

        # 基本设定
        if "基本设定" in world_setting:
            basic = world_setting["基本设定"]
            text += f"世界：{basic.get('世界名称', '')} | "
            text += f"时代：{basic.get('时代背景', '')} | "
            text += f"特色：{basic.get('魔法体系', basic.get('科技水平', ''))}\n"

        # 主要地区
        if "地理环境" in world_setting and "主要地区" in world_setting["地理环境"]:
            regions = world_setting["地理环境"]["主要地区"]
            if regions:
                text += f"主要地区：{', '.join([r.get('名称', '') for r in regions[:3]])}\n"

        return text

    def _character_profiles_to_text(self, character_profiles: List[Dict]) -> str:
        """
        将人物设定转换为文本（简化版）
        """
        if not character_profiles:
            return "暂无人物设定。"

        text = ""
        for profile_set in character_profiles:
            if "人物设定" in profile_set and isinstance(profile_set["人物设定"], list):
                for character in profile_set["人物设定"][:3]:  # 只取前3个主要人物
                    if "基本信息" in character:
                        name = character["基本信息"].get("姓名", "无名")
                        age = character["基本信息"].get("年龄", "")
                        role = character.get("角色定位", "")
                        text += f"{name}（{age}，{role}）| "

        return text.rstrip("| ")
