"""
章节智能体 (Chapter Chronicler Agent)
负责生成章节小说内容
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.core.llm import LLMInterface, LLMResponse
from app.core.knowledge_base import KnowledgeBase
from app.config import settings

class ChapterChroniclerAgent(BaseAgent):
    """章节智能体，负责生成章节小说内容"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行章节智能体
        
        Args:
            input_data: 输入数据，包含:
                - chapter_outline: 当前章节大纲节点
                - world_setting: 世界观设定
                - character_profiles: 人物设定
                - previous_summary: 前情提要
                - kb_context: 从知识库中检索的相关上下文
                - writing_style: 写作风格
                - mode: 'generate' 生成章节内容 或 'branches' 生成剧情分支
                
        Returns:
            Dict[str, Any]: 输出数据，包含:
                - chapter_content: 生成的章节内容 (mode='generate')
                - plot_branches: 生成的剧情分支 (mode='branches')
        """
        mode = input_data.get("mode", "generate")
        
        if mode == "generate":
            return await self._generate_chapter(input_data)
        elif mode == "branches":
            return await self._generate_plot_branches(input_data)
        else:
            raise ValueError(f"不支持的模式: {mode}")
    
    async def _generate_chapter(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成章节内容 - 增强版本，支持连贯性预检查和智能重试

        Args:
            input_data: 输入数据

        Returns:
            Dict[str, Any]: 输出数据
        """
        chapter_outline = input_data.get("chapter_outline", {})
        world_setting = input_data.get("world_setting", {})
        character_profiles = input_data.get("character_profiles", [])
        previous_summary = input_data.get("previous_summary", "")
        kb_context = input_data.get("kb_context", [])
        writing_style = input_data.get("writing_style", "")
        selected_branch = input_data.get("selected_branch", {})
        previous_chapters = input_data.get("previous_chapters", [])  # 新增：前面章节
        retry_count = input_data.get("retry_count", 0)  # 新增：重试次数

        # 增强前情提要生成（使用分层上下文）
        enhanced_summary = await self._generate_enhanced_summary(previous_chapters, world_setting, character_profiles, previous_summary)

        # 构建增强的提示词
        prompt_template = """
        你是一位{writing_style}小说家，正在撰写小说的第{chapter_number}章：{chapter_title}。

        {retry_guidance}

        你的任务是根据以下信息续写：

        ## 世界观核心：
        {world_setting}

        ## 本章大纲指引：
        {chapter_outline}

        ## 主要登场人物当前状态与目标：
        {character_states}

        ## 增强前情提要 (Utilize these summaries for consistency and continuity):
        {enhanced_summary}

        ---
        ## 章节叙事策略 (Chapter Narrative Strategy):

        ### 1. 小说整体节奏与当前章节定位 (Long-form Novel Pacing and Chapter Role):
        *   **当前小说进展 (Novel Progress)**: {novel_progress}
            *   (例如: 初期构建世界观与角色, 中期发展核心冲突, 接近高潮, 高潮后余波)
        *   **本章节类型 (Chapter Type)**: {chapter_type}
            *   (例如: 铺垫型(setup), 发展型(development), 冲突型(conflict), 高潮型(climax), 解决型(resolution), 反思型(reflection))
        *   **叙事节奏建议 (Adapt these suggestions to the specific chapter outline and narrative needs)**:
            *   **一般原则**: 根据以上定位，调整本章的叙事节奏。思考如何通过句式变化（长短句交替）、段落长短、场景转换频率、描写详略来控制节奏。
            *   **具体示例**:
                *   若 `chapter_type` 是 '铺垫型 (setup)' 且 `tension_level` 是 '低 (low)' 或 '上升中 (rising)': 节奏可稍缓。侧重于世界观细节的铺陈、人物关系的微妙互动、伏笔的巧妙植入。运用较多描述性语言，营造氛围，引导读者进入故事。
                *   若 `chapter_type` 是 '发展型 (development)' 且 `tension_level` 是 '上升中 (rising)': 节奏应稳步加快。情节开始加速，事件接踵而至，人物面临的挑战逐渐增多。可以在章节末尾设置小悬念或转折。
                *   若 `chapter_type` 是 '冲突型 (conflict)' 或 '高潮型 (climax)' 且 `tension_level` 是 '高 (high)' 或 '顶点 (peak)': 节奏应显著加快。多用短句、动词，减少不必要的修饰。场景切换可以更迅速，动作描写和紧张对话应占据主导。确保冲突得到充分展现，高潮事件带来强烈的冲击力并可能导致重要转折。
                *   若 `chapter_type` 是 '解决型 (resolution)' 或 '反思型 (reflection)' 且 `tension_level` 是 '回落 (falling)' 或 '平静 (resolution/calm)': 节奏应放缓。展现冲突后的余波，人物的情感反应和思考。可以有更多的内心独白或总结性的叙述，为下一阶段积蓄力量或提供过渡。
            *   请将这些建议视为参考，并根据具体章节大纲和创意灵活运用，最终目标是使章节节奏服务于故事的整体吸引力和表达效果。

        ### 2. 情绪张力构建与演进 (Emotional Tension and Progression):
        *   **目标情绪张力水平 (Target Tension Level)**: {tension_level}
            *   (例如: 低 - 构建期待感; 中 - 保持悬念或不安; 高 - 顶点冲突/危机; 释放 - 紧张后的平静或悲伤)
        *   **情绪管理指令**:
            *   请在本章中有意识地操控读者情绪。如果目标是“高”，则要逐步累积紧张感，直到爆发点；如果目标是“释放”，则要在激烈冲突后给予角色和读者喘息的空间，展现事件的余波和角色的情感反应。利用对话、内心独白、场景描写等手段来精确控制情绪的起伏。

        ### 3. 情节线索管理 (Plot Thread Management):
        *   **本章需处理的长期目标/线索 (Relevant Long-term Goals/Threads for this Chapter)**:
            {long_term_goals}
            *   (例如: 推进A主线任务至某阶段; 侧面展现B副线情节的进展; 提及或强化某个早期埋下的伏笔C; 引入新的悬念D为未来铺路)
        *   **线索编织指令**:
            *   根据“增强前情提要”中的长期和中期回顾，思考本章如何巧妙地推进或关联上述线索。
            *   对于主线，确保有实质进展。对于副线，可以适当穿插，保持其活跃度。
            *   如果本章适合，可以回应旧的伏笔或埋下新的伏笔。注意伏笔的自然融入，避免生硬。
            *   思考如何在本章结尾留下恰当的悬念 (hook)，吸引读者继续。

        ---
        {coherence_requirements}

        {branch_info}

        ## 核心写作要求 (Core Writing Instructions):
        1.  **严格一致性**: 严格遵循以上所有设定，特别是增强前情提要中的长期、中期和即时情境，确保故事的连贯性。参考“长期故事脉络回顾”以保证与小说整体走向一致，参考“中期剧情发展”以衔接近期重要情节，参考“最新即时情境”以确保与上一章的直接连续性。
        2.  **风格保持**: 保持 {writing_style} 风格。
        3.  **大纲指引**: 重点描写大纲指定的关键场景和互动。
        4.  **人物塑造**: 确保人物言行符合其性格、当前动机以及“主要登场人物当前状态与目标”中的描述。
        5.  **情节推进**: 推动情节向大纲指定方向发展，同时考虑“章节叙事策略”中的节奏、情绪和线索管理要求。
        6.  **沉浸式场景构建 (Immersive Scene Setting)**:
            *   **调动多重感官**: 在合适的场景中，尝试调动读者的多种感官体验，创造生动和身临其境的感觉。
            *   **视觉 (Visuals)**: 注意色彩、光影、形状、动态和人物的表情姿态。
            *   **听觉 (Sounds)**: 묘사环境噪音、特定的声响（如脚步声、风声、武器碰撞声）、对话的语气语调。
            *   **嗅觉 (Smells)**: 适当加入环境中的气味（如森林的清新、城市的烟火气、特定食物或花草的香气）。
            *   **触觉 (Tactile)**: 묘사物体表面的质感（粗糙、光滑、冰冷、温暖）、温度变化、风的拂过或雨的触感。
            *   **味觉 (Taste)**: 在用餐或特定情境下，可适时加入味觉描写。
            *   **自然融入**: 这些感官细节应自然地融入叙事，服务于场景氛围和人物感受，避免机械堆砌。
        7.  **字数**: 约 {word_count} 字。
        8.  **完整性**: 章节内容要完整，包含开头、发展和结尾，并考虑章节在整体叙事中的作用。
        9.  **叙事质量**: 运用生动的描写、恰当的对话和合理的节奏，提升章节的可读性和吸引力。

        请开始撰写本章内容：
        """
        
        # 提取章节信息
        chapter_number = chapter_outline.get("number", 1)
        chapter_title = chapter_outline.get("title", "")
        
        # 提取章节大纲详情
        chapter_outline_text = f"章节标题: {chapter_title}\n"
        chapter_outline_text += f"主要场景: {chapter_outline.get('scenes', '')}\n"
        chapter_outline_text += f"核心事件: {chapter_outline.get('events', '')}\n"
        chapter_outline_text += f"目标与冲突: {chapter_outline.get('conflicts', '')}\n"
        chapter_outline_text += f"关键转折点: {chapter_outline.get('turning_points', '')}\n"
        chapter_outline_text += f"情感基调: {chapter_outline.get('emotional_tone', '')}\n"
        chapter_outline_text += f"伏笔/悬念: {chapter_outline.get('foreshadowing', '')}\n"
        
        # 提取世界观设定
        world_setting_text = self._extract_relevant_world_setting(world_setting, chapter_outline)
        
        # 提取人物状态
        character_states_text = self._extract_character_states(character_profiles, chapter_outline)
        
        # 提取知识库上下文
        kb_context_text = "\n".join([f"- {item.get('text', '')}" for item in kb_context])

        # 分支信息
        branch_info = ""
        if selected_branch:
            branch_info = f"""
            ## 选定的剧情走向：
            {selected_branch.get('description', '')}

            影响：{selected_branch.get('impact', '')}
            """

        # 重试指导
        retry_guidance = ""
        if retry_count > 0:
            retry_guidance = f"""
            ## 重试指导（第{retry_count + 1}次生成）：
            前面的生成可能存在连贯性或质量问题，请特别注意：
            1. 确保与前面章节的逻辑连贯性
            2. 保持人物性格和行为的一致性
            3. 遵循世界观设定和规则
            4. 提高文笔质量和叙事节奏
            """

        # 连贯性要求
        coherence_requirements = ""
        if previous_chapters:
            coherence_requirements = """
            ## 连贯性要求：
            1. 确保时间线的连续性和合理性
            2. 人物的情感状态和关系发展要符合前面章节的铺垫
            3. 世界观元素的使用要与已建立的设定保持一致
            4. 情节发展要有逻辑性，避免突兀的转折
            """

        # 预计字数
        word_count = chapter_outline.get("word_count", settings.DEFAULT_CHAPTER_LENGTH)

        # Placeholder values for new inputs, to be replaced by actual data from input_data when available
        novel_progress = input_data.get("novel_progress", "未指定小说整体进展") # e.g., "故事初期", "中期发展", "接近高潮"
        chapter_type = input_data.get("chapter_type", "未指定章节类型") # e.g., "铺垫", "冲突", "解谜"
        tension_level = input_data.get("tension_level", "未指定情绪张力") # e.g., "低 - 构建期待", "高 - 顶点冲突"
        long_term_goals = input_data.get("long_term_goals", "未指定长期目标/线索") # e.g., "推进主角A的任务", "揭示反派B的动机"


        prompt = await self._generate_prompt(prompt_template, {
            "writing_style": writing_style,
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "retry_guidance": retry_guidance,
            "world_setting": world_setting_text,
            "chapter_outline": chapter_outline_text,
            "character_states": character_states_text,
            "enhanced_summary": enhanced_summary, # This is the formatted string from _generate_enhanced_summary
            "novel_progress": novel_progress,
            "chapter_type": chapter_type,
            "tension_level": tension_level,
            "long_term_goals": long_term_goals,
            "coherence_requirements": coherence_requirements,
            "branch_info": branch_info,
            "word_count": word_count
        })
        
        # 调用LLM生成章节内容
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=settings.CHAPTER_MAX_TOKENS,
            top_p=0.9
        )

        # 添加调试日志
        print(f"章节生成响应: {response.text[:200]}...")

        # 确保返回的内容不为空
        chapter_content = response.text.strip() if response.text else ""
        if not chapter_content:
            chapter_content = "章节内容生成失败，请重试。"
            print("警告: 章节内容为空，使用默认内容")

        return {
            "chapter_content": chapter_content
        }
    
    async def _generate_plot_branches(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成剧情分支
        
        Args:
            input_data: 输入数据
            
        Returns:
            Dict[str, Any]: 输出数据
        """
        chapter_outline = input_data.get("chapter_outline", {})
        world_setting = input_data.get("world_setting", {})
        character_profiles = input_data.get("character_profiles", [])
        previous_summary = input_data.get("previous_summary", "")
        kb_context = input_data.get("kb_context", [])
        
        # 构建提示词
        prompt_template = """
        你是一位经验丰富的小说策划师。当前小说已经发展到第{chapter_number}章，即将面临重大剧情转折点。
        
        请根据以下信息，设计3个不同的剧情分支选项：
        
        ## 世界观核心：
        {world_setting}
        
        ## 本章大纲指引：
        {chapter_outline}
        
        ## 主要人物当前状态与动机：
        {character_states}
        
        ## 前情提要：
        {previous_summary}
        
        ## 关键转折点：
        {turning_points}
        
        请设计3个截然不同但都合理的剧情走向选项，每个选项包含：
        1. 简短标题（10字以内）
        2. 详细描述（100-200字）
        3. 选择该选项对后续故事的影响（100-200字）
        4. 该选项与哪些角色的动机和性格最契合
        
        请按照以下格式输出：
        
        # 选项1：[标题]
        
        ## 描述
        [详细描述]
        
        ## 影响
        [对后续故事的影响]
        
        ## 契合角色
        [角色名称及原因]
        
        # 选项2：[标题]
        ...以此类推
        
        # 选项3：[标题]
        ...以此类推
        """
        
        # 提取章节信息
        chapter_number = chapter_outline.get("number", 1)
        chapter_title = chapter_outline.get("title", "")
        
        # 提取章节大纲详情
        chapter_outline_text = f"章节标题: {chapter_title}\n"
        chapter_outline_text += f"主要场景: {chapter_outline.get('scenes', '')}\n"
        chapter_outline_text += f"核心事件: {chapter_outline.get('events', '')}\n"
        chapter_outline_text += f"目标与冲突: {chapter_outline.get('conflicts', '')}\n"
        
        # 提取世界观设定
        world_setting_text = self._extract_relevant_world_setting(world_setting, chapter_outline)
        
        # 提取人物状态
        character_states_text = self._extract_character_states(character_profiles, chapter_outline)
        
        # 提取转折点
        turning_points = chapter_outline.get("turning_points", "")
        
        prompt = await self._generate_prompt(prompt_template, {
            "chapter_number": chapter_number,
            "world_setting": world_setting_text,
            "chapter_outline": chapter_outline_text,
            "character_states": character_states_text,
            "previous_summary": previous_summary,
            "turning_points": turning_points
        })
        
        # 调用LLM生成剧情分支
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.8,
            max_tokens=settings.PLOT_BRANCHES_MAX_TOKENS,
            top_p=0.9
        )
        
        # 解析响应，提取剧情分支
        plot_branches = self._parse_plot_branches(response.text)
        
        return {
            "plot_branches": plot_branches
        }
    
    def _extract_relevant_world_setting(self, world_setting: Dict[str, Any], chapter_outline: Dict[str, Any]) -> str:
        """
        提取与当前章节相关的世界观设定
        
        Args:
            world_setting: 世界观设定
            chapter_outline: 章节大纲
            
        Returns:
            str: 相关世界观设定文本
        """
        if not world_setting:
            return ""
            
        # 简单实现，实际应用中应该使用RAG从知识库中检索相关设定
        relevant_text = f"世界观特色: {world_setting.get('description', '')}\n\n"
        
        # 提取可能相关的部分
        sections = world_setting.get("sections", {})
        
        # 优先提取地理环境和主要势力/组织
        if "地理环境" in sections:
            relevant_text += f"地理环境:\n{sections['地理环境']}\n\n"
        
        if "主要势力/组织" in sections:
            relevant_text += f"主要势力/组织:\n{sections['主要势力/组织']}\n\n"
        
        # 如果章节涉及特殊能力，添加能量体系/科技水平
        if "能力" in str(chapter_outline) or "魔法" in str(chapter_outline) or "科技" in str(chapter_outline):
            if "能量体系/科技水平" in sections:
                relevant_text += f"能量体系/科技水平:\n{sections['能量体系/科技水平']}\n\n"
        
        return relevant_text
    
    def _extract_character_states(self, character_profiles: List[Dict[str, Any]], chapter_outline: Dict[str, Any]) -> str:
        """
        提取与当前章节相关的人物状态
        
        Args:
            character_profiles: 人物设定
            chapter_outline: 章节大纲
            
        Returns:
            str: 人物状态文本
        """
        if not character_profiles or not character_profiles[0].get("characters"):
            return ""
            
        # 获取章节中出场的人物
        appearing_characters = []
        if chapter_outline.get("characters"):
            appearing_text = chapter_outline.get("characters", "")
            # 尝试分割人物列表
            for separator in [",", "，", ";", "；", "、"]:
                if separator in appearing_text:
                    appearing_characters = [c.strip() for c in appearing_text.split(separator) if c.strip()]
                    break
            else:
                # 如果没有分隔符，将整个字符串作为一个人物
                appearing_characters = [appearing_text.strip()]
        
        # 提取相关人物信息
        character_states_text = ""
        
        for character in character_profiles[0].get("characters", []):
            name = character.get("name", "")
            
            # 如果有明确的出场人物列表，只包含出场人物
            if appearing_characters and not any(name in char for char in appearing_characters):
                continue
                
            character_states_text += f"### {name}\n"
            character_states_text += f"基本信息: {character.get('basic_info', '')}\n"
            character_states_text += f"性格: {character.get('personality', '')}\n"
            character_states_text += f"能力: {character.get('abilities', '')}\n"
            character_states_text += f"动机与目标: {character.get('motivations', '')}\n"
            character_states_text += f"与其他人物关系: {character.get('relationships', '')}\n\n"
        
        return character_states_text
    
    def _parse_plot_branches(self, text: str) -> List[Dict[str, Any]]:
        """
        从LLM响应中解析出剧情分支
        
        Args:
            text: LLM响应文本
            
        Returns:
            List[Dict[str, Any]]: 剧情分支列表
        """
        plot_branches = []
        
        # 按"# 选项"分割
        branch_texts = text.split("# 选项")
        
        # 跳过第一个空部分（如果存在）
        for i, branch_text in enumerate(branch_texts[1:], 1):
            if not branch_text.strip():
                continue
                
            # 提取标题
            title_parts = branch_text.split("\n", 1)
            title = title_parts[0].strip()
            
            # 去除标题中的序号和冒号
            if "：" in title or ":" in title:
                title = title.replace("：", ":").split(":", 1)[1].strip()
            
            # 创建分支对象
            branch = {
                "id": i,
                "title": title,
                "description": "",
                "impact": "",
                "characters": ""
            }
            
            # 提取描述
            if "## 描述" in branch_text:
                branch["description"] = self._extract_section(branch_text, "## 描述")
            
            # 提取影响
            if "## 影响" in branch_text:
                branch["impact"] = self._extract_section(branch_text, "## 影响")
            
            # 提取契合角色
            if "## 契合角色" in branch_text:
                branch["characters"] = self._extract_section(branch_text, "## 契合角色")
            
            plot_branches.append(branch)
        
        return plot_branches
    
    def _extract_section(self, text: str, section_marker: str) -> str:
        """
        从文本中提取特定部分的内容
        
        Args:
            text: 文本
            section_marker: 部分标记
            
        Returns:
            str: 提取的内容
        """
        if section_marker not in text:
            return ""
            
        parts = text.split(section_marker, 1)[1].split("##", 1)
        return parts[0].strip()

    async def _generate_enhanced_summary(self, previous_chapters: List[Dict], world_setting: Dict, character_profiles: List[Dict], basic_summary: str) -> str:
        """
        生成增强的前情提要，整合多层次上下文信息

        Args:
            previous_chapters: 前面章节
            world_setting: 世界观设定
            character_profiles: 人物设定
            basic_summary: 基础前情提要

        Returns:
            str: 增强的前情提要
        """
        if not previous_chapters:
            return "这是故事的开始。\n\n" + basic_summary

        # 使用 ContextSynthesizerAgent 生成分层上下文
        from app.agents.context_synthesizer import ContextSynthesizerAgent

        context_agent = ContextSynthesizerAgent(llm=self.llm)

        layered_context = await context_agent.run({
            "chapters": previous_chapters,
            "world_setting": world_setting,
            "character_profiles": character_profiles,
            "mode": "layered"
        })

        # 整合分层上下文和基础前情提要
        # The 'summary' key from layered_context is the comprehensive summary
        # The other keys are the distinct layers. We want to pass these distinct layers
        # clearly to the chapter generation prompt.

        long_term = layered_context.get('long_term_summary', '无长期发展脉络信息。')
        medium_term = layered_context.get('medium_summary', '无中期剧情发展信息。')
        recent_term = layered_context.get('recent_summary', '无近期即时情境信息。')
        comprehensive_summary = layered_context.get('summary', basic_summary) # Fallback to basic_summary if not found

        # Format these summaries into a structured string for the chapter prompt
        formatted_enhanced_summary = f"""
### 长期故事脉络回顾 (Long-Term Context):
{long_term}

### 中期剧情发展 (Medium-Term Context - Last 5-10 Chapters):
{medium_term}

### 最新即时情境 (Recent Context - Last 1-3 Chapters):
{recent_term}

### 综合前情提要 (Overall Summary for this Chapter):
{comprehensive_summary}
"""
        # If basic_summary is different and provides more details (e.g. user-provided), consider appending it or integrating it.
        # For now, the comprehensive_summary from layered_context is expected to be sufficient.
        # If basic_summary is crucial and distinct, it could be added:
        # if basic_summary and basic_summary not in comprehensive_summary:
        #    formatted_enhanced_summary += f"\n## 补充前情提要:\n{basic_summary}"

        return formatted_enhanced_summary.strip()
