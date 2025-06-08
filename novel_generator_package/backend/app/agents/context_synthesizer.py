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
        # 1. 长期上下文（贯穿整个小说的主要情节线、人物发展和伏笔）
        long_term_context = await self._build_long_term_context(chapters, key_events, character_states, world_setting, character_profiles)

        # 2. 中期上下文（近期章节的关键事件）
        medium_context = await self._build_medium_context(chapters, key_events)

        # 3. 即时上下文（上一章的直接影响）
        immediate_context = await self._build_immediate_context(chapters)

        # 4. 综合前情提要
        comprehensive_summary = await self._build_comprehensive_summary(long_term_context, medium_context, immediate_context)

        return {
            "summary": comprehensive_summary,
            "long_term_summary": long_term_context, # Updated key
            "medium_summary": medium_context, # Updated key
            "recent_summary": immediate_context # Updated key
        }

    async def _build_long_term_context(self, chapters: List[Dict], key_events: List, character_states: Dict, world_setting: Dict, character_profiles: List[Dict]) -> str:
        """
        构建长期上下文（贯穿整个小说的主要情节线、人物发展和伏笔）
        """
        prompt_template = """你是一位资深的小说编辑。请根据以下提供的整个故事至今的全部章节、关键事件、人物状态、世界观和人物设定，生成一份长期的故事发展总结（约400-600字）。这份总结应该追踪主要的剧情线索，关键人物的成长与变化，以及作者埋下的重要伏笔和尚未解决的谜团。

## 世界观设定：
{world_setting_text}

## 主要人物设定：
{character_profiles_text}

## 至今的全部章节摘要：
{chapters_summary_text}

## 关键事件回顾：
{key_events_text}

## 主要人物当前状态：
{character_states_text}

请综合以上所有信息，生成一份长期的故事发展总结。重点分析：
1.  **主要剧情线索**：识别并总结故事中的核心情节线，它们是如何发展的？目前进展到哪个阶段？
2.  **关键人物发展**：主要人物（特别是主角）经历了哪些重要的成长、转变或学到了什么？他们的目标和动机有何变化？
3.  **伏笔与谜团**：作者在故事中埋下了哪些重要的伏笔？有哪些尚未解开的谜团或悬念？这些对未来情节可能产生什么影响？
4.  **主题与基调**：故事到目前为止展现了哪些核心主题？整体基调是怎样的？

这份总结的目的是为了让创作者（或AI助手）能够清晰地把握故事的全貌和长期走向，确保后续章节的创作能够与前面内容保持一致性和连贯性。请确保总结的深度和广度，而不仅仅是表面事件的罗列。
"""

        world_setting_text = self._world_setting_to_text(world_setting)
        character_profiles_text = self._character_profiles_to_text(character_profiles)

        # For long-term context, we might want to summarize chapters differently, perhaps focusing on outcomes and major turns.
        # For now, let's use a simpler summary.
        chapters_summary_text = ""
        if chapters:
            # Summarize each chapter briefly to keep the prompt manageable
            for chapter in chapters:
                title = chapter.get("title", f"第{chapter.get('chapter_number', '')}章")
                content = chapter.get("content", "")
                # Create a very brief summary or use existing chapter summaries if available
                summary = content[:100] + "..." if len(content) > 100 else content
                chapters_summary_text += f"{title}: {summary}\n"
        else:
            chapters_summary_text = "目前还没有章节内容。"

        key_events_text = self._key_events_to_text(key_events)
        character_states_text = self._character_states_to_text(character_states)

        prompt = await self._generate_prompt(prompt_template, {
            "world_setting_text": world_setting_text,
            "character_profiles_text": character_profiles_text,
            "chapters_summary_text": chapters_summary_text,
            "key_events_text": key_events_text,
            "character_states_text": character_states_text
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.5, # Slightly higher for more abstract summarization
            max_tokens=800, # Allow for a more detailed summary
            top_p=settings.AGENT_TOP_P
        )

        return response.text.strip()

    async def _build_medium_context(self, chapters: List[Dict], key_events: List) -> str:
        """
        构建中期上下文（近期章节的关键事件）
        """
        if not chapters:
            return "这是故事的开始，还没有中期发展。"

        # 取最近5-10章
        # Determine the range of chapters to consider for medium-term context
        num_chapters = len(chapters)
        if num_chapters == 0:
            return "这是故事的开始，还没有中期发展。"

        start_index = max(0, num_chapters - 10) # Start from at most 10 chapters ago
        if num_chapters <= 5: # If 5 or fewer chapters, take all of them
             medium_term_chapters = chapters
        else: # if more than 5 chapters, take last 5 to 10.
            start_index = max(0, num_chapters - 10)
            # Ensure we take at least 5 if possible, up to 10.
            actual_start_index = min(start_index, num_chapters - 5) if num_chapters > 5 else 0
            medium_term_chapters = chapters[actual_start_index:]


        prompt_template = """你是一位敏锐的剧情分析师。请根据以下最近5至10个章节的内容以及已知的关键事件，生成一份中期剧情回顾（约300-500字）。这份回顾应该聚焦于这段时期内的关键情节进展、主要人物的行动和心路历程变化、以及重要的冲突和解决方案。

## 近期章节（最近5-10章）：
{medium_term_chapters_text}

## 已知关键事件（可能部分与近期章节重叠）：
{key_events_text}

请重点分析并总结：
1.  **核心情节推进**：在这些章节中，主线或重要的次线情节有哪些实质性的进展？关键的转折点是什么？
2.  **角色弧光**：主要人物在这段时间内经历了哪些挑战？他们的目标、动机或人际关系有何变化？是否有明显的角色成长或转变的迹象？
3.  **关键冲突与解决**：这段时期内出现了哪些主要的冲突？它们是如何被解决的，或者目前进展到什么状态？
4.  **伏笔与铺垫**：这些章节中是否为未来的剧情埋下了新的伏笔或进行了铺垫？

这份中期回顾的目的是为了在不回顾整个故事的前提下，快速把握最近一段时间的核心动态，为接下来的创作承上启下。
"""

        medium_term_chapters_text = ""
        for chapter in medium_term_chapters:
            title = chapter.get("title", f"第{chapter.get('chapter_number', '')}章")
            content = chapter.get("content", "")
            # 提取章节摘要，可以稍微详细一点
            summary = content[:200] + "..." if len(content) > 200 else content
            medium_term_chapters_text += f"{title}：{summary}\n\n"

        key_events_text = self._key_events_to_text(key_events) # Consider filtering key events relevant to this period if possible

        prompt = await self._generate_prompt(prompt_template, {
            "medium_term_chapters_text": medium_term_chapters_text,
            "key_events_text": key_events_text # Pass all key events for now, LLM can pick relevant ones
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.4,
            max_tokens=600, # Increased token limit for a more detailed summary
            top_p=settings.AGENT_TOP_P
        )

        return response.text.strip()

    async def _build_immediate_context(self, chapters: List[Dict]) -> str:
        """
        构建即时上下文（上一章的直接影响）
        """
        if not chapters:
            return "故事即将开始，尚无即时情节。"

        # Consider last 1-3 chapters for immediate context
        num_chapters = len(chapters)
        if num_chapters == 0:
            return "故事即将开始，尚无即时情节。"

        immediate_chapters_count = min(num_chapters, 3) # Take up to 3 chapters
        recent_chapters_for_immediate = chapters[-immediate_chapters_count:]

        prompt_template = """你是一位专注于当前时刻的叙事助手。请根据最近1至3个章节的内容，生成一份即时情境回顾（约150-250字）。这份回顾需要精准捕捉故事最新进展、人物的即时状态、以及直接引导下一章节的悬念或任务。

## 最近章节（最后1-3章）：
{recent_chapters_text}

请重点总结：
1.  **最新事件**：刚刚发生了什么核心事件？故事线索推进到了哪里？
2.  **人物即时状态**：主要人物（特别是视角人物）目前的情绪、位置、健康状况、以及他们下一步最可能采取的行动是什么？
3.  **直接悬念/任务**：当前是否存在未解的悬念、迫在眉睫的危机、或角色需要立即着手的任务？
4.  **对下一章的铺垫**：最新章节的结局是如何为下一章的开篇做铺垫的？

这份即时回顾的目的是为了确保新章节能够紧密衔接当前剧情，保持故事的即时连贯性和紧张感。
"""

        recent_chapters_text = ""
        for chapter in recent_chapters_for_immediate:
            title = chapter.get("title", f"第{chapter.get('chapter_number', '')}章")
            content = chapter.get("content", "")
            summary = content[:500] + "..." if len(content) > 500 else content # Allow slightly more content for immediate context
            recent_chapters_text += f"### {title}\n{summary}\n\n"

        prompt = await self._generate_prompt(prompt_template, {
            "recent_chapters_text": recent_chapters_text
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=300, # Adjusted for a 150-250 word summary
            top_p=settings.AGENT_TOP_P
        )

        return response.text.strip()

    async def _build_comprehensive_summary(self, long_term_context: str, medium_context: str, recent_context: str) -> str:
        """
        构建综合前情提要
        """
        prompt_template = """你是一位小说前情提要专家。请根据以下提供的长期故事脉络、中期剧情发展以及最新的即时情境，编织一个全面且引人入胜的前情提要（建议500字左右，可根据内容调整）。这份提要需要无缝整合各个时间维度的信息，为读者（或AI写手）提供一个清晰、连贯的故事背景，确保新章节的创作能够自然融入整体叙事。

## 长期故事脉络回顾：
(这部分总结了整个故事至今的主要情节线、核心人物的长期发展、以及重要的伏笔和主题)
{long_term_context}

## 中期剧情发展：
(这部分聚焦于最近5-10个章节的关键情节、人物弧光和冲突演变)
{medium_context}

## 最新即时情境：
(这部分概括了最后1-3个章节的核心事件、人物当前状态和直接面临的悬念或任务)
{recent_context}

请综合以上三个层面的信息，撰写一份引人入胜的前情提要。要求：
1.  **无缝整合**：自然地将长期、中期和即时信息融合在一起，形成一个连贯的叙述流程。
2.  **突出重点**：强调对理解当前故事节点最重要的信息，如主要人物的核心目标、当前的危机、重要的未解之谜等。
3.  **引导创作**：提要的结尾应当能够自然地引导至下一章节的开端，暗示读者或AI写手接下来可能发生什么。
4.  **保持风格**：尽量贴合小说的叙事风格和基调。
5.  **字数控制**：目标500字左右，但可根据信息量灵活调整，确保内容的完整性和吸引力。

请使用**加粗**来高亮显示关键的人物、地点、事件或悬念。
"""

        prompt = await self._generate_prompt(prompt_template, {
            "long_term_context": long_term_context,
            "medium_context": medium_context,
            "recent_context": recent_context # Ensure key matches
        })

        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.4, # Keep it balanced
            max_tokens=700, # Allow for a comprehensive summary
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
