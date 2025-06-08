"""
内容审核智能体，负责审核小说章节内容
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class ContentIntegrityAgent(BaseAgent):
    """内容审核智能体 - 增强版本，支持连贯性检查和质量控制"""

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行内容审核智能体

        Args:
            input_data: 输入数据，包含：
                - chapter_content: 生成的章节文本
                - chapter_outline: 章节大纲
                - character_profiles: 人物设定
                - kb_snapshot: 知识库快照
                - writing_style: 预设风格
                - previous_chapters: 前面章节内容（用于连贯性检查）
                - world_setting: 世界观设定（用于一致性检查）
                - mode: 检查模式 'full'(完整检查) 或 'coherence'(连贯性检查)

        Returns:
            Dict[str, Any]: 输出数据，包含：
                - total_score: 总评分(0-100)
                - dimension_scores: 各维度评分
                - audit_report: 审核报告
                - coherence_issues: 连贯性问题列表
                - quality_threshold_passed: 是否通过质量阈值
                - improvement_suggestions: 改进建议
        """
        chapter_content = input_data.get("chapter_content", "")
        chapter_outline = input_data.get("chapter_outline", {})
        character_profiles = input_data.get("character_profiles", [])
        kb_snapshot = input_data.get("kb_snapshot", {})
        writing_style = input_data.get("writing_style", "")
        previous_chapters = input_data.get("previous_chapters", [])
        world_setting = input_data.get("world_setting", {})
        mode = input_data.get("mode", "full")

        # 根据模式选择不同的检查方式
        if mode == "coherence":
            return await self._check_coherence_only(chapter_content, previous_chapters, character_profiles, world_setting)
        else:
            return await self._full_content_audit(chapter_content, chapter_outline, character_profiles, kb_snapshot, writing_style, previous_chapters, world_setting)

    async def _check_coherence_only(self, chapter_content: str, previous_chapters: List[Dict], character_profiles: List[Dict], world_setting: Dict) -> Dict[str, Any]:
        """
        仅进行连贯性检查（用于章节生成前的预检查）
        """
        prompt_template = """你是一位专业的小说连贯性分析师。请重点检查以下章节内容的连贯性问题：

## 检查维度：
1. **角色行为一致性**：角色的行为、对话、性格是否与之前章节保持一致
2. **情节逻辑连贯性**：情节发展是否符合逻辑，与前面章节是否有矛盾
3. **世界观一致性**：是否违反了已建立的世界观设定和规则
4. **时间线连贯性**：时间顺序和事件发展是否合理

## 前面章节摘要：
{previous_summary}

## 人物设定：
{character_info}

## 世界观设定：
{world_setting_info}

## 当前章节内容：
{chapter_content}

请按照以下JSON格式输出连贯性检查结果：

{{
  "coherence_score": 分数(0-100),
  "coherence_issues": [
    {{
      "type": "角色行为一致性/情节逻辑连贯性/世界观一致性/时间线连贯性",
      "description": "具体问题描述",
      "severity": "high/medium/low",
      "suggestion": "修改建议"
    }}
  ],
  "overall_assessment": "整体连贯性评估",
  "pass_threshold": true/false
}}
"""

        # 构建前面章节摘要
        previous_summary = self._build_previous_summary(previous_chapters)
        character_info = self._character_profiles_to_text(character_profiles)
        world_setting_info = self._world_setting_to_text(world_setting)

        prompt = await self._generate_prompt(prompt_template, {
            "previous_summary": previous_summary,
            "character_info": character_info,
            "world_setting_info": world_setting_info,
            "chapter_content": chapter_content
        })

        # 调用LLM进行连贯性检查
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,  # 较低温度确保一致性
            max_tokens=settings.AGENT_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )

        try:
            import json
            result = json.loads(response.text)

            # 添加质量阈值判断（连贯性分数需要达到70分以上）
            quality_threshold_passed = result.get("coherence_score", 0) >= 70
            result["quality_threshold_passed"] = quality_threshold_passed

            return result
        except json.JSONDecodeError:
            # 如果解析失败，返回默认结果
            return {
                "coherence_score": 50,
                "coherence_issues": [{"type": "解析错误", "description": "无法解析LLM响应", "severity": "high", "suggestion": "重新生成"}],
                "overall_assessment": "连贯性检查失败",
                "pass_threshold": False,
                "quality_threshold_passed": False
            }

    async def _full_content_audit(self, chapter_content: str, chapter_outline: Dict, character_profiles: List[Dict], kb_snapshot: Dict, writing_style: str, previous_chapters: List[Dict], world_setting: Dict) -> Dict[str, Any]:
        """
        完整的内容审核（包含连贯性检查和质量评估）
        """
        # 先进行连贯性检查
        coherence_result = await self._check_coherence_only(chapter_content, previous_chapters, character_profiles, world_setting)

        # 构建完整审核提示词
        prompt_template = """你是一位细致的小说校对和内容分析师。请根据以下标准评估这段章节内容，每个维度10分，总分100分：

1.  **逻辑连贯性 (Logical Coherence)** (10分): 情节发展是否符合逻辑，与前文、大纲、知识库设定是否矛盾？
2.  **情节吸引力 (Plot Engagement)** (10分): 情节是否引人入胜，能否激发读者阅读兴趣？是否有恰当的悬念和节奏？
3.  **人物塑造一致性 (Character Consistency)** (10分): 人物言行是否符合其已建立的性格、动机及过往行为？
4.  **世界观契合度 (World Setting Alignment)** (10分): 内容是否与已设定的世界观（规则、氛围、背景）保持一致？
5.  **写作风格与流畅度 (Writing Style & Fluency)** (10分): 是否与预设的 {writing_style} 风格保持一致？文笔是否流畅自然？
6.  **对话自然度与功能性 (Dialogue Naturalness & Functionality)** (10分): 对话是否自然且符合人物身份？是否有效推动情节或揭示人物性格？
7.  **整体可读性 (Overall Readability)** (10分): 章节整体阅读体验如何？结构是否清晰？
8.  **创新性 (Innovativeness)** (10分): 情节、角色或设定是否有新颖之处？是否避免了常见的陈词滥调？
9.  **情感深度 (Emotional Depth)** (10分): 角色情感是否真实可信？能否引发读者的情感投入？场景氛围是否营造到位？
10. **角色弧光完整性 (Character Arc Completeness)** (10分): 主要角色在本章中是否有所发展或变化（即使是微小的），是否为其整体弧光做出贡献或铺垫？

章节内容:
{chapter_content}

章节大纲:
{chapter_outline_text}

人物设定:
{character_profiles_text}

知识库相关信息:
{kb_snapshot_text}

预设风格:
{writing_style}

请为每个维度打分（按权重），并给出总评和具体问题点。在提供“具体问题点”和“改进建议”时，请确保它们是具体且可操作的，以便用于指导后续的修订。请按照以下JSON格式输出：

{{
  "dimension_scores": {{
    "逻辑连贯性": 分数,
    "情节吸引力": 分数,
    "人物一致性": 分数,
    "世界观契合度": 分数,
    "写作风格与流畅度": 分数,
    "对话自然度与功能性": 分数,
    "整体可读性": 分数,
    "创新性": 分数,
    "情感深度": 分数,
    "角色弧光完整性": 分数
  }},
  "total_score": 总分, // 应为100
  "audit_report": {{
    "总体评价": "总体评价内容...",
    "具体问题点": [
      "问题1：详细描述...",
      "问题2：详细描述...",
      ...
    ],
    "改进建议": [
      "建议1",
      "建议2",
      ...
    ]
  }}
}}
"""
        
        # 将章节大纲转换为文本
        chapter_outline_text = self._chapter_outline_to_text(chapter_outline)
        
        # 将人物设定转换为文本
        character_profiles_text = self._character_profiles_to_text(character_profiles)
        
        # 将知识库快照转换为文本
        kb_snapshot_text = self._kb_snapshot_to_text(kb_snapshot)
        
        prompt = await self._generate_prompt(prompt_template, {
            "chapter_content": chapter_content,
            "chapter_outline_text": chapter_outline_text,
            "character_profiles_text": character_profiles_text,
            "kb_snapshot_text": kb_snapshot_text,
            "writing_style": writing_style
        })
        
        # 调用LLM评估章节内容
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,
            max_tokens=settings.AGENT_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )
        
        # 解析结果
        import json
        import re
        
        try:
            # 使用正则表达式提取JSON部分
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # 解析JSON
                result = json.loads(json_str)
                return result
            else:
                # 如果无法提取JSON，返回默认结果
                return {
                    "dimension_scores": {
                        "情节一致性": 0,
                        "人物一致性": 0,
                        "风格一致性": 0,
                        "写作风格与流畅度": 0,
                        "对话自然度与功能性": 0,
                        "整体可读性": 0,
                        "创新性": 0,
                        "情感深度": 0,
                        "角色弧光完整性": 0
                    },
                    "total_score": 0,
                    "audit_report": {
                        "总体评价": "无法解析评估结果",
                        "具体问题点": ["无法提供具体问题点"],
                        "改进建议": ["无法提供改进建议"]
                    }
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "dimension_scores": {
                    "逻辑连贯性": 0,
                    "情节吸引力": 0,
                    "人物一致性": 0,
                    "世界观契合度": 0,
                    "写作风格与流畅度": 0,
                    "对话自然度与功能性": 0,
                    "整体可读性": 0,
                    "创新性": 0,
                    "情感深度": 0,
                    "角色弧光完整性": 0
                },
                "total_score": 0,
                "audit_report": {
                    "总体评价": f"解析评估结果时出错: {str(e)}",
                    "具体问题点": ["无法提供具体问题点"],
                    "改进建议": ["无法提供改进建议"]
                }
            }
    
    def _chapter_outline_to_text(self, chapter_outline: Dict[str, Any]) -> str:
        """
        将章节大纲转换为文本
        
        Args:
            chapter_outline: 章节大纲
            
        Returns:
            str: 文本形式的章节大纲
        """
        text = ""
        
        if "标题" in chapter_outline:
            text += f"章节标题: {chapter_outline['标题']}\n"
        
        if "核心内容" in chapter_outline:
            core_content = chapter_outline["核心内容"]
            
            if "主要场景" in core_content:
                text += f"主要场景: {', '.join(core_content['主要场景'])}\n"
            
            if "出场人物" in core_content:
                text += f"出场人物: {', '.join(core_content['出场人物'])}\n"
            
            if "核心事件" in core_content:
                text += f"核心事件: {core_content['核心事件']}\n"
            
            if "目标与冲突" in core_content:
                text += f"目标与冲突: {core_content['目标与冲突']}\n"
            
            if "关键转折点" in core_content:
                text += f"关键转折点: {core_content['关键转折点']}\n"
            
            if "情感基调" in core_content:
                text += f"情感基调: {core_content['情感基调']}\n"
            
            if "伏笔或悬念" in core_content:
                text += f"伏笔或悬念: {core_content['伏笔或悬念']}\n"
        
        return text
    
    def _character_profiles_to_text(self, character_profiles: List[Dict[str, Any]]) -> str:
        """
        将人物设定转换为文本
        
        Args:
            character_profiles: 人物设定
            
        Returns:
            str: 文本形式的人物设定
        """
        text = ""
        
        for profile_set in character_profiles:
            # 如果是原始文本，直接添加
            if "raw_text" in profile_set:
                text += profile_set["raw_text"] + "\n\n"
                continue
            
            # 否则，将结构化数据转换为文本
            if "人物设定" in profile_set and isinstance(profile_set["人物设定"], list):
                for character in profile_set["人物设定"]:
                    # 基本信息
                    if "基本信息" in character:
                        text += f"【{character['基本信息'].get('姓名', '无名')}】\n"
                        text += f"性别: {character['基本信息'].get('性别', '')}\n"
                        text += f"年龄: {character['基本信息'].get('年龄', '')}\n"
                        text += f"种族: {character['基本信息'].get('种族', '')}\n"
                    
                    # 性格特质
                    if "性格特质" in character:
                        text += "性格特质:\n"
                        text += f"  核心性格: {character['性格特质'].get('核心性格', '')}\n"
                        text += f"  优点: {', '.join(character['性格特质'].get('优点', []))}\n"
                        text += f"  缺点: {', '.join(character['性格特质'].get('缺点', []))}\n"
                    
                    # 动机与目标
                    if "动机与目标" in character:
                        text += "动机与目标:\n"
                        text += f"  内心驱动力: {character['动机与目标'].get('内心驱动力', '')}\n"
                        text += f"  短期目标: {character['动机与目标'].get('短期目标', '')}\n"
                        text += f"  长期目标: {character['动机与目标'].get('长期目标', '')}\n"
                    
                    text += "\n"
        
        return text
    
    def _kb_snapshot_to_text(self, kb_snapshot: Dict[str, Any]) -> str:
        """
        将知识库快照转换为文本
        
        Args:
            kb_snapshot: 知识库快照
            
        Returns:
            str: 文本形式的知识库快照
        """
        # 简单实现，实际应用中需要更复杂的逻辑
        text = ""
        
        # 实体信息
        if "entities" in kb_snapshot:
            text += "【实体信息】\n"
            for entity_id, entity in kb_snapshot["entities"].items():
                text += f"- {entity.get('name', entity_id)}: {entity.get('description', '')}\n"
            text += "\n"
        
        # 关系信息
        if "relationships" in kb_snapshot:
            text += "【关系信息】\n"
            for relationship in kb_snapshot["relationships"]:
                source_id = relationship.get("source_id", "")
                target_id = relationship.get("target_id", "")
                rel_type = relationship.get("type", "")
                text += f"- {source_id} {rel_type} {target_id}\n"
            text += "\n"
        
        # 事件信息
        if "events" in kb_snapshot:
            text += "【事件信息】\n"
            for event in kb_snapshot["events"]:
                text += f"- {event.get('description', '')}\n"
            text += "\n"
        
        return text

    def _build_previous_summary(self, previous_chapters: List[Dict]) -> str:
        """
        构建前面章节的摘要
        """
        if not previous_chapters:
            return "这是第一章，没有前面的章节。"

        summary = "前面章节摘要：\n"
        # 只取最近3章，避免内容过长
        recent_chapters = previous_chapters[-3:] if len(previous_chapters) > 3 else previous_chapters

        for i, chapter in enumerate(recent_chapters):
            chapter_num = chapter.get("chapter_number", i + 1)
            title = chapter.get("title", f"第{chapter_num}章")
            content = chapter.get("content", "")

            # 提取章节摘要（前200字）
            chapter_summary = content[:200] + "..." if len(content) > 200 else content
            summary += f"\n第{chapter_num}章 {title}：\n{chapter_summary}\n"

        return summary

    def _world_setting_to_text(self, world_setting: Dict) -> str:
        """
        将世界观设定转换为文本
        """
        if not world_setting:
            return "暂无世界观设定。"

        text = "世界观设定：\n"

        # 基本设定
        if "基本设定" in world_setting:
            basic = world_setting["基本设定"]
            text += f"世界名称: {basic.get('世界名称', '')}\n"
            text += f"时代背景: {basic.get('时代背景', '')}\n"
            text += f"科技水平: {basic.get('科技水平', '')}\n"
            text += f"魔法体系: {basic.get('魔法体系', '')}\n"

        # 地理环境
        if "地理环境" in world_setting:
            geo = world_setting["地理环境"]
            if "主要地区" in geo:
                text += "\n主要地区：\n"
                for region in geo["主要地区"]:
                    text += f"- {region.get('名称', '')}: {region.get('描述', '')}\n"

        # 社会结构
        if "社会结构" in world_setting:
            social = world_setting["社会结构"]
            text += f"\n政治制度: {social.get('政治制度', '')}\n"
            text += f"社会阶层: {social.get('社会阶层', '')}\n"

        return text
