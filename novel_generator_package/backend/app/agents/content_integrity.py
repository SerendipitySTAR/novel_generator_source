"""
内容审核智能体，负责审核小说章节内容
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class ContentIntegrityAgent(BaseAgent):
    """内容审核智能体"""
    
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
            
        Returns:
            Dict[str, Any]: 输出数据，包含：
                - total_score: 总评分(0-100)
                - dimension_scores: 各维度评分
                - audit_report: 审核报告
        """
        chapter_content = input_data.get("chapter_content", "")
        chapter_outline = input_data.get("chapter_outline", {})
        character_profiles = input_data.get("character_profiles", [])
        kb_snapshot = input_data.get("kb_snapshot", {})
        writing_style = input_data.get("writing_style", "")
        
        # 构建提示词
        prompt_template = """你是一位细致的小说校对和内容分析师。请根据以下标准评估这段章节内容：

1. 情节一致性（20分）：与前文、大纲、知识库设定是否矛盾？
2. 人物一致性（20分）：人物言行是否符合其性格、动机及过往行为？
3. 风格一致性（15分）：是否与预设的{writing_style}风格保持一致？
4. 高潮精彩程度（15分）：如有高潮，是否营造到位，是否符合预期？
5. 整体章节质量（15分）：文笔流畅度、描写生动性、叙事节奏
6. 剧情推动程度（15分）：是否有效推进故事，达成章节目标？
7. 可读性/趣味性（10分，可选）：主观评估章节的可读性和趣味性

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

请为每个维度打分（按权重），并给出总评和具体问题点。请按照以下JSON格式输出：

{{
  "dimension_scores": {{
    "情节一致性": 分数,
    "人物一致性": 分数,
    "风格一致性": 分数,
    "高潮精彩程度": 分数,
    "整体章节质量": 分数,
    "剧情推动程度": 分数,
    "可读性/趣味性": 分数
  }},
  "total_score": 总分,
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
                        "高潮精彩程度": 0,
                        "整体章节质量": 0,
                        "剧情推动程度": 0,
                        "可读性/趣味性": 0
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
                    "情节一致性": 0,
                    "人物一致性": 0,
                    "风格一致性": 0,
                    "高潮精彩程度": 0,
                    "整体章节质量": 0,
                    "剧情推动程度": 0,
                    "可读性/趣味性": 0
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
