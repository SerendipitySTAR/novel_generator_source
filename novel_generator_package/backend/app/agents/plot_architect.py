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
                - narrative_concept: 小说概述
                - world_setting: 世界观设定
                - conflict_elements: 关键冲突元素
                - chapter_count: 章节数量
                - num_outlines: 需要生成的大纲数量
                
        Returns:
            Dict[str, Any]: 输出数据，包含:
                - plot_outlines: 生成的章节大纲列表
        """
        narrative_concept = input_data.get("narrative_concept", "")
        world_setting = input_data.get("world_setting", {})
        conflict_elements = input_data.get("conflict_elements", [])
        chapter_count = input_data.get("chapter_count", 10)
        num_outlines = input_data.get("num_outlines", 1)
        
        # 将世界观设定转换为文本
        world_setting_text = self._world_setting_to_text(world_setting)
        
        # 构建提示词
        prompt_template = """
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
        4. 如果是多线叙事，请标明各故事线的章节分布与交叉点
        
        请特别注意情节的逻辑性、节奏感（张弛有度）、高潮的铺垫与爆发，以及多线叙事（如果适用）的平衡与交织。
        
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
        
        ## 章节详情
        
        ### 第1章: [章节标题]
        - 主要场景: [详细内容]
        - 出场人物: [详细内容]
        - 核心事件: [详细内容]
        - 目标与冲突: [详细内容]
        - 关键转折点: [详细内容]
        - 情感基调: [详细内容]
        - 伏笔/悬念: [详细内容]
        
        ### 第2章: [章节标题]
        ...以此类推
        
        # 大纲版本2
        ...以此类推
        """
        
        # 将关键冲突元素转换为文本
        conflict_elements_text = "\n".join([f"- {element}" for element in conflict_elements])
        
        prompt = await self._generate_prompt(prompt_template, {
            "chapter_count": chapter_count,
            "num_outlines": num_outlines,
            "narrative_concept": narrative_concept,
            "world_setting": world_setting_text,
            "conflict_elements": conflict_elements_text
        })
        
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
                "chapters": [],
                "chapter_details": []
            }
            
            # 提取总体故事结构
            if "## 总体故事结构" in outline_text:
                structure_parts = outline_text.split("## 总体故事结构", 1)[1].split("##", 1)
                outline["structure"] = structure_parts[0].strip()
            
            # 提取章节列表
            if "## 章节列表" in outline_text:
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
                        chapter_detail["scenes"] = self._extract_content(chapter_content, "- 主要场景:")
                    if "- 出场人物:" in chapter_content:
                        chapter_detail["characters"] = self._extract_content(chapter_content, "- 出场人物:")
                    if "- 核心事件:" in chapter_content:
                        chapter_detail["events"] = self._extract_content(chapter_content, "- 核心事件:")
                    if "- 目标与冲突:" in chapter_content:
                        chapter_detail["conflicts"] = self._extract_content(chapter_content, "- 目标与冲突:")
                    if "- 关键转折点:" in chapter_content:
                        chapter_detail["turning_points"] = self._extract_content(chapter_content, "- 关键转折点:")
                    if "- 情感基调:" in chapter_content:
                        chapter_detail["emotional_tone"] = self._extract_content(chapter_content, "- 情感基调:")
                    if "- 伏笔/悬念:" in chapter_content or "- 伏笔或悬念设置:" in chapter_content:
                        chapter_detail["foreshadowing"] = self._extract_content(chapter_content, "- 伏笔/悬念:") or self._extract_content(chapter_content, "- 伏笔或悬念设置:")
                    
                    chapter_details.append(chapter_detail)
                
                outline["chapter_details"] = chapter_details
            
            plot_outlines.append(outline)
        
        return plot_outlines
    
    def _extract_content(self, text: str, marker: str) -> str:
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
