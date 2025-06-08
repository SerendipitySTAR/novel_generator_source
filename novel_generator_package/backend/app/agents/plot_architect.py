"""
大纲智能体 (Plot Architect Agent)
负责生成小说章节大纲
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.core.llm import LLMInterface, LLMResponse
from app.core.knowledge_base import KnowledgeBase
from app.config import settings

class PlotArchitectAgent(BaseAgent):
    """大纲智能体，负责生成小说章节大纲"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行大纲智能体
        
        Args:
            input_data: 输入数据，包含:
                - narrative_concept: 小说概述 (for default mode)
                - world_setting: 世界观设定 (for default mode, context for expansion mode)
                - conflict_elements: 关键冲突元素 (for default mode)
                - chapter_count: 章节数量
                - num_outlines: 需要生成的大纲数量
                - mode: "default" or "expand_core_ideas" (Optional, defaults to "default")
                - core_ideas: List[str] (Required if mode is "expand_core_ideas")
                
        Returns:
            Dict[str, Any]: 输出数据，包含:
                - plot_outlines: 生成的章节大纲列表
        """
        mode = input_data.get("mode", "default")
        core_ideas = input_data.get("core_ideas")
        chapter_count = input_data.get("chapter_count", 10)
        num_outlines = input_data.get("num_outlines", 1) # num_outlines might be less relevant for core_ideas mode or could mean variations.

        narrative_concept = input_data.get("narrative_concept", "")
        world_setting = input_data.get("world_setting", {})
        conflict_elements = input_data.get("conflict_elements", [])
        
        world_setting_text = self._world_setting_to_text(world_setting)
        conflict_elements_text = "\n".join([f"- {element}" for element in conflict_elements])

        prompt_data = {
            "chapter_count": chapter_count,
            "num_outlines": num_outlines,
            "narrative_concept": narrative_concept,
            "world_setting": world_setting_text,
            "conflict_elements": conflict_elements_text,
            "core_ideas": "\n".join([f"{i+1}. {idea}" for i, idea in enumerate(core_ideas)]) if core_ideas else ""
        }

        if mode == "expand_core_ideas" and core_ideas:
            prompt_template_to_use = self._get_expansion_prompt_template()
        else:
            prompt_template_to_use = self._get_default_prompt_template()

        prompt = await self._generate_prompt(prompt_template_to_use, prompt_data)

        # 调用LLM生成大纲
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=settings.PLOT_OUTLINE_MAX_TOKENS,
            top_p=0.9
        )
        
        # 解析响应，提取大纲
        plot_outlines = self._parse_plot_outlines(response.text)

        return {
            "plot_outlines": plot_outlines
        }

    def _get_default_prompt_template(self) -> str:
        return """
        你是一位经验丰富的小说编辑和情节规划师。基于以下小说概述和世界观设定，并围绕指定的关键冲突元素，请规划一份包含约{chapter_count}章节的详细小说大纲。请提供{num_outlines}个版本。

        每个版本应包含:
        
        1. 总体故事结构图（如三幕式、英雄之旅等）
        2. 各章节列表，包含:
           - 章节号
           - 章节主题/标题
           - 预计字数
        3. 每章核心内容:
           - 主要场景
           - 出场人物
           - 核心事件/情节
           - 目标与冲突
           - 关键转折点
           - 情感基调
           - 伏笔或悬念设置
        
        ## 叙事结构与多线叙事 (Narrative Structure & Multi-Line Narratives)
        请设计一个主线情节和1-2个重要的次要情节线（B线/C线）。
        - 主线情节：[简述主线核心发展脉络]
        - 次要情节线1：[简述其核心发展及与主线的关联]
        - (可选) 次要情节线2：[简述其核心发展及与主线的关联]
        - 情节线交织点：明确指出各情节线在哪些关键章节或事件中交汇、相互影响或形成对比。

        ## 主题深度 (Thematic Depth)
        - 核心主题：[明确小说希望探讨的1-3个核心主题，例如：正义与牺牲、科技伦理的边界、身份认同的追寻、背叛与救赎等]
        - 主题呈现：简述这些主题将如何通过主要事件、角色行为或冲突来体现，避免说教，力求自然融入。

        ## 关键情节转折 (Key Plot Twists)
        - 情节转折点1：[描述一个重要的情节转折，它应如何颠覆预期但又在情理之中？何时发生？]
        - (可选) 情节转折点2：[描述另一个情节转折，如有。]
        - 伏笔铺垫：简要说明为这些转折点埋下了哪些伏笔。

        ## 整体叙事节奏与张力控制 (Overall Narrative Pacing and Tension Control)
        在设计章节大纲时，请确保整体叙事节奏的动态变化和张力的起伏。故事应自然地经历以下阶段：
        *   **铺垫与阐述 (Setup/Exposition):** 介绍人物、世界观及初步冲突。
        *   **上升行动 (Rising Action):** 逐步增加风险，发展冲突，提升紧张感。
        *   **中点/不归点 (Mid-Point/Point of No Return):** 发生重大事件，改变故事走向，主角无法回头。
        *   **高潮 (Climax):** 紧张和冲突达到顶点，主要矛盾面临关键对决。
        *   **下降行动 (Falling Action):** 处理高潮的直接后果。
        *   **结局/尾声 (Resolution/Denouement):** 解主线冲突，展示新的平衡状态。
        请在每个主要情节线（主线、副线）的梗概中，简要说明其如何对应这些叙事阶段。并在章节概要中，适当提示放置高度悬念、激烈动作或宁静反思/角色塑造的时刻。

        ## 悬念与信息控制 (Suspense & Information Control)
        为构建复杂的悬念，可以考虑运用以下技巧：
        *   **戏剧性反讽 (Dramatic Irony):** 让读者比角色更早了解某些关键信息。
        *   **延迟揭示 (Delayed Revelations):** 将关键信息保留到最具冲击力的时刻再揭晓。
        *   **误导 (Misdirection):** 引导读者或角色产生错误判断。
        *   **多视角叙事 (Multiple POVs):** (如果适用) 通过不同角色的视角控制信息流，营造悬念。
        请在章节概要中，简要标注何处可能运用这些悬念技巧。

        请特别注意情节的逻辑性、节奏感（张弛有度）、高潮的铺垫与爆发，以及多线叙事的平衡与交织。
        
        小说概述:
        {narrative_concept}
        
        世界观设定:
        {world_setting}
        
        关键冲突元素:
        {conflict_elements}
        
        请按照以下格式输出，为每个大纲版本添加编号:
        
        # 大纲版本1
        
        ## 总体故事结构
        [详细内容]
        
        ## 章节列表
        1. [章节标题] - [预计字数]
        2. [章节标题] - [预计字数]
        ...

        ## 叙事结构与多线叙事详情
        ### 主线情节
        [详细描述主线发展]
        ### 次要情节线1: [名称]
        [详细描述B线发展及其与主线的交织点]
        ### (可选) 次要情节线2: [名称]
        [详细描述C线发展及其与主线的交织点]

        ## 主题探讨
        [详细说明主题如何在故事中呈现]

        ## 关键情节转折设计
        ### 情节转折点1: [名称/简述]
        - 发生章节/时机:
        - 具体描述:
        - 前期伏笔:
        ### (可选) 情节转折点2: [名称/简述]
        - 发生章节/时机:
        - 具体描述:
        - 前期伏笔:
        
        ## 章节详情
        
        ### 第1章: [章节标题]
        - 主要场景: [详细内容]
        - 出场人物: [详细内容]
        - 核心事件: [详细内容] (涉及哪些情节线？ pacing: fast/slow, tension: rising/falling)
        - 目标与冲突: [详细内容]
        - 关键转折点: [详细内容]
        - 情感基调: [详细内容]
        - 伏笔/悬念: [详细内容] (为后续哪些情节线或转折铺垫？ suspense_technique: e.g., dramatic_irony_hint)
        
        ### 第2章: [章节标题]
        ...以此类推
        
        # 大纲版本2
        ...以此类推
        """

    def _get_expansion_prompt_template(self) -> str:
        return """
        你是一位富有创造力的小说策划大师。根据以下提供的核心创意点子，请将它们扩展成一个引人入胜的、包含约{chapter_count}章节的小说大纲框架。

        核心创意点子:
        {core_ideas}

        请围绕这些核心点子，完成以下任务：
        1.  **提炼核心概念**：从这些点子中提炼出一个统一且吸引人的核心故事概念。
        2.  **构建叙事弧光**：设计一个初步的叙事弧光，包括开端、发展、高潮和结局。明确每个阶段如何体现或推进核心创意。
        3.  **关键角色建议**：初步设想1-3个与核心创意紧密相关的关键角色。他们的主要动机和在故事中的作用是什么？
        4.  **主要冲突设计**：基于核心创意，设定故事的主要冲突（内部/外部）。
        5.  **潜在转折点**：构思1-2个可能的关键转折点，这些转折点应与核心创意相关。
        6.  **章节概要（{chapter_count}章）**：为每一章提供简短的标题和一两句话的核心内容概要，清晰地展示核心创意如何在各章节中逐步展开和实现。

        如果提供了世界观设定，请在构思时作为参考背景：
        世界观设定参考（可选）:
        {world_setting}

        请按照以下格式输出（如果适用，可提供{num_outlines}个不同侧重点的扩展版本，用 # 大纲版本X 分隔）：

        # 大纲版本1 (基于核心创意扩展)

        ## 核心故事概念
        [根据核心创意提炼的故事核心概念]

        ## 初步叙事弧光
        - 开端: [描述，并说明如何体现核心创意]
        - 发展: [描述，并说明如何体现核心创意]
        - 高潮: [描述，并说明如何体现核心创意]
        - 结局: [描述，并说明如何体现核心创意]

        ## 关键角色建议
        - 角色1: [姓名/类型，动机，作用，与核心创意的关联]
        - 角色2: [姓名/类型，动机，作用，与核心创意的关联]

        ## 主要冲突
        [描述主要冲突，以及它如何源于或服务于核心创意]

        ## 潜在转折点
        - 转折点1: [描述，与核心创意的关联]

        ## 各章节概要
        1.  [章节标题]: [核心内容概要，体现核心创意]
        2.  [章节标题]: [核心内容概要，体现核心创意]
        ...
        """

    def _world_setting_to_text(self, world_setting: Dict[str, Any]) -> str:
        """
        将世界观设定转换为文本
        
        Args:
            world_setting: 世界观设定
            
        Returns:
            str: 世界观设定文本
        """
        if not world_setting:
            return ""
            
        text = f"世界观特色: {world_setting.get('description', '')}\n\n"
        
        for section_name, section_content in world_setting.get("sections", {}).items():
            text += f"{section_name}:\n{section_content}\n\n"
        
        return text
    
    def _parse_plot_outlines(self, text: str) -> List[Dict[str, Any]]:
        """
        从LLM响应中解析出大纲列表
        
        Args:
            text: LLM响应文本
            
        Returns:
            List[Dict[str, Any]]: 大纲列表
        """
        plot_outlines = []
        
        # 按"# 大纲版本"分割
        outline_texts = text.split("# 大纲版本")
        
        # 跳过第一个空部分（如果存在）
        for outline_text in outline_texts[1:]:
            if not outline_text.strip():
                continue
                
            # 解析大纲内容
            outline = {
                "version": outline_text.split("\n", 1)[0].strip(),
                "structure": "",
                "narrative_structure_and_plotlines": {}, # New field
                "thematic_depth": "", # New field
                "key_plot_twists": [], # New field
                "chapters": [],
                "chapter_details": []
            }
            
            # Helper function to extract section content
            def extract_section_content(text, marker):
                if f"## {marker}" in text:
                    return text.split(f"## {marker}", 1)[1].split("## ", 1)[0].strip()
                return ""

            outline["structure"] = extract_section_content(outline_text, "总体故事结构")

            # New sections parsing
            narrative_details_text = extract_section_content(outline_text, "叙事结构与多线叙事详情")
            if narrative_details_text:
                # This parsing can be made more sophisticated if needed
                outline["narrative_structure_and_plotlines"] = {
                    "raw_text": narrative_details_text, # Store raw for now, or parse further
                    "main_plot": self._extract_subsection_content(narrative_details_text, "### 主线情节"),
                    "subplot_1": self._extract_subsection_content(narrative_details_text, "### 次要情节线1"),
                    "subplot_2": self._extract_subsection_content(narrative_details_text, "### 次要情节线2")
                }

            outline["thematic_depth"] = extract_section_content(outline_text, "主题探讨")

            twists_text = extract_section_content(outline_text, "关键情节转折设计")
            if twists_text:
                # Simple parsing for twists, can be enhanced
                twist_parts = twists_text.split("### 情节转折点")
                for part in twist_parts[1:]:
                    part = part.strip()
                    if not part: continue
                    twist_name = part.split("\n",1)[0].strip()
                    outline["key_plot_twists"].append({
                        "name": twist_name,
                        "details": part # Store raw details for now
                    })

            # 提取章节列表
            if "## 章节列表" in outline_text: # Keep this specific check as it's distinct
                chapters_part = outline_text.split("## 章节列表", 1)[1].split("##", 1)[0].strip()
                chapter_lines = chapters_part.split("\n")
                
                for line in chapter_lines:
                    line = line.strip()
                    if line and line[0].isdigit():
                        # 解析章节信息
                        chapter_info = {
                            "number": int(line.split(".", 1)[0].strip()),
                            "title": "",
                            "word_count": 0
                        }
                        
                        # 提取标题和字数
                        title_parts = line.split(".", 1)[1].strip()
                        if "-" in title_parts:
                            title, word_count = title_parts.rsplit("-", 1)
                            chapter_info["title"] = title.strip()
                            # 尝试提取字数
                            try:
                                chapter_info["word_count"] = int(''.join(filter(str.isdigit, word_count)))
                            except:
                                pass
                        else:
                            chapter_info["title"] = title_parts
                        
                        outline["chapters"].append(chapter_info)
            
            # 提取章节详情
            if "## 章节详情" in outline_text:
                details_part = outline_text.split("## 章节详情", 1)[1].strip()
                chapter_details = []
                
                # 按"### 第X章"分割
                chapter_parts = details_part.split("### 第")
                
                for part in chapter_parts[1:]:  # 跳过第一个空部分
                    # 解析章节号和标题
                    chapter_header = part.split("\n", 1)[0].strip()
                    chapter_number = int(chapter_header.split("章:", 1)[0].strip())
                    chapter_title = chapter_header.split("章:", 1)[1].strip() if "章:" in chapter_header else ""
                    
                    # 解析章节内容
                    chapter_content = part.split("\n", 1)[1].strip() if len(part.split("\n", 1)) > 1 else ""
                    
                    # 提取各项内容
                    chapter_detail = {
                        "number": chapter_number,
                        "title": chapter_title,
                        "scenes": "",
                        "characters": "",
                        "events": "",
                        "conflicts": "",
                        "turning_points": "",
                        "emotional_tone": "",
                        "foreshadowing": ""
                    }
                    
                    # 解析各项内容
                    if "- 主要场景:" in chapter_content:
                        chapter_detail["scenes"] = self._extract_subsection_content(chapter_content, "- 主要场景:")
                    if "- 出场人物:" in chapter_content:
                        chapter_detail["characters"] = self._extract_subsection_content(chapter_content, "- 出场人物:")
                    if "- 核心事件:" in chapter_content:
                        chapter_detail["events"] = self._extract_subsection_content(chapter_content, "- 核心事件:")
                    if "- 目标与冲突:" in chapter_content:
                        chapter_detail["conflicts"] = self._extract_subsection_content(chapter_content, "- 目标与冲突:")
                    if "- 关键转折点:" in chapter_content:
                        chapter_detail["turning_points"] = self._extract_subsection_content(chapter_content, "- 关键转折点:")
                    if "- 情感基调:" in chapter_content:
                        chapter_detail["emotional_tone"] = self._extract_subsection_content(chapter_content, "- 情感基调:")
                    if "- 伏笔/悬念:" in chapter_content or "- 伏笔或悬念设置:" in chapter_content: # Existing
                        foreshadowing_content = self._extract_subsection_content(chapter_content, "- 伏笔/悬念:")
                        if not foreshadowing_content: # Try alternative marker
                             foreshadowing_content = self._extract_subsection_content(chapter_content, "- 伏笔或悬念设置:")
                        chapter_detail["foreshadowing"] = foreshadowing_content
                    
                    chapter_details.append(chapter_detail)
                
                outline["chapter_details"] = chapter_details
            
            plot_outlines.append(outline)
        
        return plot_outlines
    
    def _extract_subsection_content(self, text: str, marker: str) -> str: # Renamed from _extract_content
        """
        从文本中提取特定标记后的内容
        
        Args:
            text: 文本
            marker: 标记
            
        Returns:
            str: 提取的内容
        """
        if marker not in text:
            return ""
            
        parts = text.split(marker, 1)[1].split("\n- ", 1)
        return parts[0].strip() if len(parts) > 0 else ""
