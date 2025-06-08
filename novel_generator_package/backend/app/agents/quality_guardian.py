"""
质量审核智能体，负责审核小说概述、世界观、大纲、人物设定
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class QualityGuardianAgent(BaseAgent):
    """质量审核智能体 - 增强版本，支持量化质量指标和多轮审核"""

    # 质量阈值配置
    QUALITY_THRESHOLDS = {
        "concept": 75,      # 概述质量阈值
        "world_setting": 80, # 世界观质量阈值
        "plot_outline": 85,  # 大纲质量阈值
        "character_profiles": 80, # 人物设定质量阈值
        "chapter": 75       # 章节质量阈值
    }

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行质量审核智能体

        Args:
            input_data: 输入数据，包含：
                - content_type: 内容类型，可以是"concept"(概述)、"world_setting"(世界观)、"plot_outline"(大纲)、"character_profiles"(人物设定)、"chapter"(章节)
                - content: 需要审核的内容
                - context: 上下文信息（可选）
                - retry_count: 重试次数（用于多轮审核）

        Returns:
            Dict[str, Any]: 输出数据，包含：
                - total_score: 总评分(0-100)
                - dimension_scores: 各维度评分
                - evaluation_reasons: 评分理由
                - improvement_suggestions: 改进建议
                - quality_threshold_passed: 是否通过质量阈值
                - detailed_metrics: 详细量化指标
                - retry_recommended: 是否建议重试
        """
        content_type = input_data.get("content_type", "")
        content = input_data.get("content", {})
        context = input_data.get("context", {})
        retry_count = input_data.get("retry_count", 0)

        # 根据内容类型进行评估
        if content_type == "concept":
            result = await self._evaluate_narrative_concept(content, context)
        elif content_type == "world_setting":
            result = await self._evaluate_world_setting(content, context)
        elif content_type == "plot_outline":
            result = await self._evaluate_plot_outline(content, context)
        elif content_type == "character_profiles":
            result = await self._evaluate_character_profiles(content, context)
        elif content_type == "chapter":
            result = await self._evaluate_chapter_content(content, context)
        else:
            raise ValueError(f"不支持的内容类型: {content_type}")

        # 添加质量阈值判断
        threshold = self.QUALITY_THRESHOLDS.get(content_type, 75)
        total_score = result.get("total_score", 0)
        quality_threshold_passed = total_score >= threshold

        # 添加重试建议
        retry_recommended = not quality_threshold_passed and retry_count < 2

        # 增强结果
        result.update({
            "quality_threshold_passed": quality_threshold_passed,
            "retry_recommended": retry_recommended,
            "threshold_score": threshold,
            "retry_count": retry_count,
            "detailed_metrics": self._calculate_detailed_metrics(result, content_type)
        })

        return result
    
    async def _evaluate_narrative_concept(self, concept: str, context: Dict = None) -> Dict[str, Any]:
        """
        评估小说概述

        Args:
            concept: 小说概述
            context: 上下文信息（可选）

        Returns:
            Dict[str, Any]: 评估结果
        """
        # 构建提示词
        prompt_template = """你是一位挑剔的文学评论家和资深编辑。请对以下小说概述进行全面评估。请从以下维度进行打分（每个维度25分，总分100）：

1. 情节新颖度：概念的原创性和创新程度，是否避免了陈词滥调和过度使用的情节
2. 冲突潜力：故事中设置的冲突是否有足够的张力和发展空间
3. 角色魅力潜力：概述中的角色类型是否有吸引力，是否有发展成丰满角色的潜质
4. 主题深度潜力：故事是否有探索深刻主题的可能性，是否能引发读者思考

小说概述:
{concept}

请详细说明每个维度的评分理由，并给出至少3条具体的、有建设性的修改建议，帮助提升其质量。请按照以下JSON格式输出：

{{
  "dimension_scores": {{
    "情节新颖度": 分数,
    "冲突潜力": 分数,
    "角色魅力潜力": 分数,
    "主题深度潜力": 分数
  }},
  "total_score": 总分,
  "evaluation_reasons": {{
    "情节新颖度": "评分理由...",
    "冲突潜力": "评分理由...",
    "角色魅力潜力": "评分理由...",
    "主题深度潜力": "评分理由..."
  }},
  "improvement_suggestions": [
    "具体修改建议1",
    "具体修改建议2",
    "具体修改建议3",
    ...
  ]
}}
"""
        
        prompt = await self._generate_prompt(prompt_template, {
            "concept": concept
        })
        
        # 调用LLM评估概述
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.3,  # 使用较低的温度以获得更一致的评估
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
                        "情节新颖度": 0,
                        "冲突潜力": 0,
                        "角色魅力潜力": 0,
                        "主题深度潜力": 0
                    },
                    "total_score": 0,
                    "evaluation_reasons": {
                        "error": "无法解析评估结果"
                    },
                    "improvement_suggestions": [
                        "无法提供具体建议，请检查输入内容"
                    ]
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "dimension_scores": {
                    "情节新颖度": 0,
                    "冲突潜力": 0,
                    "角色魅力潜力": 0,
                    "主题深度潜力": 0
                },
                "total_score": 0,
                "evaluation_reasons": {
                    "error": f"解析评估结果时出错: {str(e)}"
                },
                "improvement_suggestions": [
                    "无法提供具体建议，请检查输入内容"
                ]
            }
    
    async def _evaluate_world_setting(self, world_setting: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """
        评估世界观设定

        Args:
            world_setting: 世界观设定
            context: 上下文信息（可选）

        Returns:
            Dict[str, Any]: 评估结果
        """
        # 将世界观设定转换为文本
        world_setting_text = self._world_setting_to_text(world_setting)
        
        # 构建提示词
        prompt_template = """你是一位挑剔的文学评论家和资深编辑。请对以下世界观设定进行全面评估。请从以下维度进行打分（每个维度25分，总分100）：

1. 原创性：世界观的独特性和创新程度，是否避免了常见的设定和模板
2. 逻辑自洽性：世界观内部的规则和设定是否合理、一致，没有明显的逻辑漏洞
3. 细节丰富度：世界观是否有足够的细节和深度，能够支撑长篇小说的创作
4. 与主题契合度：世界观是否能够有效地服务于故事主题和情节发展

世界观设定:
{world_setting_text}

请详细说明每个维度的评分理由，并给出至少3条具体的、有建设性的修改建议，帮助提升其质量。请按照以下JSON格式输出：

{{
  "dimension_scores": {{
    "原创性": 分数,
    "逻辑自洽性": 分数,
    "细节丰富度": 分数,
    "与主题契合度": 分数
  }},
  "total_score": 总分,
  "evaluation_reasons": {{
    "原创性": "评分理由...",
    "逻辑自洽性": "评分理由...",
    "细节丰富度": "评分理由...",
    "与主题契合度": "评分理由..."
  }},
  "improvement_suggestions": [
    "具体修改建议1",
    "具体修改建议2",
    "具体修改建议3",
    ...
  ]
}}
"""
        
        prompt = await self._generate_prompt(prompt_template, {
            "world_setting_text": world_setting_text
        })
        
        # 调用LLM评估世界观
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
                        "原创性": 0,
                        "逻辑自洽性": 0,
                        "细节丰富度": 0,
                        "与主题契合度": 0
                    },
                    "total_score": 0,
                    "evaluation_reasons": {
                        "error": "无法解析评估结果"
                    },
                    "improvement_suggestions": [
                        "无法提供具体建议，请检查输入内容"
                    ]
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "dimension_scores": {
                    "原创性": 0,
                    "逻辑自洽性": 0,
                    "细节丰富度": 0,
                    "与主题契合度": 0
                },
                "total_score": 0,
                "evaluation_reasons": {
                    "error": f"解析评估结果时出错: {str(e)}"
                },
                "improvement_suggestions": [
                    "无法提供具体建议，请检查输入内容"
                ]
            }
    
    async def _evaluate_plot_outline(self, plot_outline: Dict[str, Any], context: Dict = None) -> Dict[str, Any]:
        """
        评估大纲

        Args:
            plot_outline: 大纲
            context: 上下文信息（可选）

        Returns:
            Dict[str, Any]: 评估结果
        """
        # 将大纲转换为文本
        plot_outline_text = self._plot_outline_to_text(plot_outline)
        
        # 构建提示词
        prompt_template = """你是一位挑剔的文学评论家和资深编辑。请对以下小说大纲进行全面评估。请从以下维度进行打分（每个维度25分，总分100）：

1. 情节逻辑性：情节发展是否合理、连贯，没有明显的逻辑漏洞
2. 叙事节奏：故事的节奏是否张弛有度，高潮和平缓部分是否安排合理
3. 冲突激烈度：故事中的冲突是否足够激烈，能够吸引读者
4. 伏笔与高潮分布：伏笔的埋设和高潮的安排是否合理，能够形成完整的故事弧

小说大纲:
{plot_outline_text}

请详细说明每个维度的评分理由，并给出至少3条具体的、有建设性的修改建议，帮助提升其质量。请按照以下JSON格式输出：

{{
  "dimension_scores": {{
    "情节逻辑性": 分数,
    "叙事节奏": 分数,
    "冲突激烈度": 分数,
    "伏笔与高潮分布": 分数
  }},
  "total_score": 总分,
  "evaluation_reasons": {{
    "情节逻辑性": "评分理由...",
    "叙事节奏": "评分理由...",
    "冲突激烈度": "评分理由...",
    "伏笔与高潮分布": "评分理由..."
  }},
  "improvement_suggestions": [
    "具体修改建议1",
    "具体修改建议2",
    "具体修改建议3",
    ...
  ]
}}
"""
        
        prompt = await self._generate_prompt(prompt_template, {
            "plot_outline_text": plot_outline_text
        })
        
        # 调用LLM评估大纲
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
                        "情节逻辑性": 0,
                        "叙事节奏": 0,
                        "冲突激烈度": 0,
                        "伏笔与高潮分布": 0
                    },
                    "total_score": 0,
                    "evaluation_reasons": {
                        "error": "无法解析评估结果"
                    },
                    "improvement_suggestions": [
                        "无法提供具体建议，请检查输入内容"
                    ]
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "dimension_scores": {
                    "情节逻辑性": 0,
                    "叙事节奏": 0,
                    "冲突激烈度": 0,
                    "伏笔与高潮分布": 0
                },
                "total_score": 0,
                "evaluation_reasons": {
                    "error": f"解析评估结果时出错: {str(e)}"
                },
                "improvement_suggestions": [
                    "无法提供具体建议，请检查输入内容"
                ]
            }
    
    async def _evaluate_character_profiles(self, character_profiles: List[Dict[str, Any]], context: Dict = None) -> Dict[str, Any]:
        """
        评估人物设定

        Args:
            character_profiles: 人物设定
            context: 上下文信息（可选）

        Returns:
            Dict[str, Any]: 评估结果
        """
        # 将人物设定转换为文本
        character_profiles_text = self._character_profiles_to_text(character_profiles)
        
        # 构建提示词
        prompt_template = """你是一位挑剔的文学评论家和资深编辑。请对以下人物设定进行全面评估。请从以下维度进行打分（每个维度25分，总分100）：

1. 性格鲜明度：人物性格是否鲜明、立体，避免了扁平化和刻板印象
2. 动机合理性：人物的动机和目标是否合理、清晰，与其背景和性格相符
3. 角色弧光潜力：人物是否有明确的成长空间和变化轨迹
4. 与故事契合度：人物设定是否能够有效地服务于故事主题和情节发展

人物设定:
{character_profiles_text}

请详细说明每个维度的评分理由，并给出至少3条具体的、有建设性的修改建议，帮助提升其质量。请按照以下JSON格式输出：

{{
  "dimension_scores": {{
    "性格鲜明度": 分数,
    "动机合理性": 分数,
    "角色弧光潜力": 分数,
    "与故事契合度": 分数
  }},
  "total_score": 总分,
  "evaluation_reasons": {{
    "性格鲜明度": "评分理由...",
    "动机合理性": "评分理由...",
    "角色弧光潜力": "评分理由...",
    "与故事契合度": "评分理由..."
  }},
  "improvement_suggestions": [
    "具体修改建议1",
    "具体修改建议2",
    "具体修改建议3",
    ...
  ]
}}
"""
        
        prompt = await self._generate_prompt(prompt_template, {
            "character_profiles_text": character_profiles_text
        })
        
        # 调用LLM评估人物设定
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
                        "性格鲜明度": 0,
                        "动机合理性": 0,
                        "角色弧光潜力": 0,
                        "与故事契合度": 0
                    },
                    "total_score": 0,
                    "evaluation_reasons": {
                        "error": "无法解析评估结果"
                    },
                    "improvement_suggestions": [
                        "无法提供具体建议，请检查输入内容"
                    ]
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "dimension_scores": {
                    "性格鲜明度": 0,
                    "动机合理性": 0,
                    "角色弧光潜力": 0,
                    "与故事契合度": 0
                },
                "total_score": 0,
                "evaluation_reasons": {
                    "error": f"解析评估结果时出错: {str(e)}"
                },
                "improvement_suggestions": [
                    "无法提供具体建议，请检查输入内容"
                ]
            }
    
    def _world_setting_to_text(self, world_setting: Dict[str, Any]) -> str:
        """
        将世界观设定转换为文本
        
        Args:
            world_setting: 世界观设定
            
        Returns:
            str: 文本形式的世界观设定
        """
        # 如果是原始文本，直接返回
        if "raw_text" in world_setting:
            return world_setting["raw_text"]
        
        # 否则，将结构化数据转换为文本
        text = ""
        
        # 基础设定
        if "基础设定" in world_setting:
            text += "【基础设定】\n"
            for key, value in world_setting["基础设定"].items():
                text += f"- {key}: {value}\n"
            text += "\n"
        
        # 地理环境
        if "地理环境" in world_setting:
            text += "【地理环境】\n"
            for key, value in world_setting["地理环境"].items():
                if isinstance(value, list):
                    text += f"- {key}: {', '.join(value)}\n"
                else:
                    text += f"- {key}: {value}\n"
            text += "\n"
        
        # 历史背景
        if "历史背景" in world_setting:
            text += "【历史背景】\n"
            if "重大历史事件" in world_setting["历史背景"]:
                text += "- 重大历史事件:\n"
                for event in world_setting["历史背景"]["重大历史事件"]:
                    text += f"  * {event['年代']}: {event['事件']} - {event['影响']}\n"
            
            for key, value in world_setting["历史背景"].items():
                if key != "重大历史事件" and isinstance(value, list):
                    text += f"- {key}: {', '.join(value)}\n"
            text += "\n"
        
        # 主要势力/组织
        if "主要势力/组织" in world_setting and isinstance(world_setting["主要势力/组织"], list):
            text += "【主要势力/组织】\n"
            for org in world_setting["主要势力/组织"]:
                text += f"- {org['名称']}:\n"
                text += f"  * 标志: {org['标志']}\n"
                text += f"  * 理念: {org['理念']}\n"
                text += f"  * 领袖: {org['领袖']}\n"
                text += f"  * 核心成员: {', '.join(org['核心成员'])}\n"
                text += f"  * 实力评估: {org['实力评估']}\n"
                text += f"  * 控制区域: {', '.join(org['控制区域'])}\n"
                if "外交关系" in org:
                    text += f"  * 同盟: {', '.join(org['外交关系'].get('同盟', []))}\n"
                    text += f"  * 敌对: {', '.join(org['外交关系'].get('敌对', []))}\n"
            text += "\n"
        
        # 能量体系/科技水平
        if "能量体系/科技水平" in world_setting:
            text += "【能量体系/科技水平】\n"
            text += f"- 类型: {world_setting['能量体系/科技水平']['类型']}\n"
            text += f"- 详细描述: {world_setting['能量体系/科技水平']['详细描述']}\n"
            text += f"- 主要派系/分支: {', '.join(world_setting['能量体系/科技水平']['主要派系/分支'])}\n"
            text += f"- 使用条件/限制: {', '.join(world_setting['能量体系/科技水平']['使用条件/限制'])}\n"
            text += f"- 禁忌/危险: {', '.join(world_setting['能量体系/科技水平']['禁忌/危险'])}\n"
            text += "\n"
        
        # 文化与社会
        if "文化与社会" in world_setting:
            text += "【文化与社会】\n"
            for key, value in world_setting["文化与社会"].items():
                if isinstance(value, list):
                    text += f"- {key}: {', '.join(value)}\n"
                else:
                    text += f"- {key}: {value}\n"
            text += "\n"
        
        # 特殊生物/物种
        if "特殊生物/物种" in world_setting and isinstance(world_setting["特殊生物/物种"], list):
            text += "【特殊生物/物种】\n"
            for species in world_setting["特殊生物/物种"]:
                text += f"- {species['名称']}:\n"
                text += f"  * 习性: {species['习性']}\n"
                text += f"  * 能力: {', '.join(species['能力'])}\n"
                text += f"  * 与人类关系: {species['与人类关系']}\n"
            text += "\n"
        
        return text
    
    def _plot_outline_to_text(self, plot_outline: Dict[str, Any]) -> str:
        """
        将大纲转换为文本
        
        Args:
            plot_outline: 大纲
            
        Returns:
            str: 文本形式的大纲
        """
        # 如果是原始文本，直接返回
        if "raw_text" in plot_outline:
            return plot_outline["raw_text"]
        
        # 否则，将结构化数据转换为文本
        text = ""
        
        # 故事结构
        if "故事结构" in plot_outline:
            text += f"故事结构: {plot_outline['故事结构']}\n\n"
        
        # 章节列表
        if "章节列表" in plot_outline and isinstance(plot_outline["章节列表"], list):
            text += "章节列表:\n"
            for chapter in plot_outline["章节列表"]:
                text += f"第{chapter['章节号']}章: {chapter['标题']} (约{chapter['预计字数']}字)\n"
                if "核心内容" in chapter:
                    text += f"  主要场景: {', '.join(chapter['核心内容'].get('主要场景', []))}\n"
                    text += f"  出场人物: {', '.join(chapter['核心内容'].get('出场人物', []))}\n"
                    text += f"  核心事件: {chapter['核心内容'].get('核心事件', '')}\n"
                    text += f"  目标与冲突: {chapter['核心内容'].get('目标与冲突', '')}\n"
                    text += f"  关键转折点: {chapter['核心内容'].get('关键转折点', '')}\n"
                    text += f"  情感基调: {chapter['核心内容'].get('情感基调', '')}\n"
                    text += f"  伏笔或悬念: {chapter['核心内容'].get('伏笔或悬念', '')}\n"
            text += "\n"
        
        # 多线叙事
        if "多线叙事" in plot_outline and isinstance(plot_outline["多线叙事"], list):
            text += "多线叙事:\n"
            for storyline in plot_outline["多线叙事"]:
                text += f"- {storyline['故事线名称']}:\n"
                text += f"  涉及章节: {', '.join(map(str, storyline['涉及章节']))}\n"
                text += f"  主要人物: {', '.join(storyline['主要人物'])}\n"
                text += f"  核心冲突: {storyline['核心冲突']}\n"
            text += "\n"
        
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
                        text += f"外貌特征: {', '.join(character['基本信息'].get('外貌特征', []))}\n"
                        text += f"衣着风格: {character['基本信息'].get('衣着风格', '')}\n"
                    
                    # 背景故事
                    if "背景故事" in character:
                        text += f"背景故事: {character['背景故事']}\n"
                    
                    # 性格特质
                    if "性格特质" in character:
                        text += "性格特质:\n"
                        text += f"  核心性格: {character['性格特质'].get('核心性格', '')}\n"
                        text += f"  价值观: {character['性格特质'].get('价值观', '')}\n"
                        text += f"  优点: {', '.join(character['性格特质'].get('优点', []))}\n"
                        text += f"  缺点: {', '.join(character['性格特质'].get('缺点', []))}\n"
                        text += f"  癖好: {character['性格特质'].get('癖好', '')}\n"
                        text += f"  口头禅: {character['性格特质'].get('口头禅', '')}\n"
                    
                    # 能力技能
                    if "能力技能" in character:
                        text += "能力技能:\n"
                        text += f"  技能: {', '.join(character['能力技能'].get('技能', []))}\n"
                        text += f"  知识: {', '.join(character['能力技能'].get('知识', []))}\n"
                        text += f"  特殊能力: {character['能力技能'].get('特殊能力', '')}\n"
                        text += f"  力量等级: {character['能力技能'].get('力量等级', '')}\n"
                    
                    # 动机与目标
                    if "动机与目标" in character:
                        text += "动机与目标:\n"
                        text += f"  内心驱动力: {character['动机与目标'].get('内心驱动力', '')}\n"
                        text += f"  短期目标: {character['动机与目标'].get('短期目标', '')}\n"
                        text += f"  长期目标: {character['动机与目标'].get('长期目标', '')}\n"
                    
                    # 角色弧光
                    if "角色弧光" in character:
                        text += f"角色弧光: {character['角色弧光']}\n"
                    
                    # 人际关系
                    if "人际关系" in character and isinstance(character["人际关系"], list):
                        text += "人际关系:\n"
                        for relation in character["人际关系"]:
                            text += f"  与{relation['关系对象']}的关系: {relation['关系类型']} - {relation['关系描述']}\n"
                    
                    text += "\n"
            
            # 人物关系图谱
            if "人物关系图谱" in profile_set:
                text += f"人物关系图谱: {profile_set['人物关系图谱']}\n\n"
        
        return text

    async def _evaluate_chapter_content(self, chapter_content: str, context: Dict = None) -> Dict[str, Any]:
        """
        评估章节内容

        Args:
            chapter_content: 章节内容
            context: 上下文信息（包含前面章节、人物设定、世界观等）

        Returns:
            Dict[str, Any]: 评估结果
        """
        # 构建提示词
        prompt_template = """你是一位挑剔的文学评论家和资深编辑。请对以下章节内容进行全面评估。请从以下维度进行打分（每个维度20分，总分100）：

1. 情节连贯性：章节内容是否与前面章节逻辑连贯，没有明显的情节漏洞 (20分)
2. 人物一致性：人物的行为、对话、性格是否与设定保持一致 (20分)
3. 文笔质量：语言表达是否流畅、生动，文字功底是否扎实 (20分)
4. 节奏把控：章节的叙事节奏是否合适，张弛有度 (20分)
5. 情感渲染：是否能够有效地传达情感，引起读者共鸣 (20分)

在进行上述评估时，请特别针对章节内容，额外深入思考以下几个方面，并将这些思考融入到你的评分理由和修改建议中：
*   **创新性 (Innovativeness)**：章节中的情节、角色互动或设定细节是否有新颖之处？是否有效避免了常见的陈词滥调？
*   **情感深度 (Emotional Depth)**：角色情感的描绘是否真实可信、有层次感？场景氛围是否能够有效地烘托和增强情感表达，引发读者的深层情感投入？
*   **角色弧光进展 (Character Arc Progression)**：主要角色在本章中是否展现了符合其整体发展弧线的变化或成长（即使是微小的）？本章事件是否对其性格、认知或目标产生了有意义的影响或铺垫？

章节内容:
{chapter_content}

{context_info}

请详细说明每个维度的评分理由，并给出至少3条具体的、有建设性的修改建议，帮助提升其质量。请按照以下JSON格式输出：

{{
  "dimension_scores": {{
    "情节连贯性": 分数,
    "人物一致性": 分数,
    "文笔质量": 分数,
    "节奏把控": 分数,
    "情感渲染": 分数
  }},
  "total_score": 总分,
  "evaluation_reasons": {{
    "情节连贯性": "评分理由...",
    "人物一致性": "评分理由...",
    "文笔质量": "评分理由...",
    "节奏把控": "评分理由...",
    "情感渲染": "评分理由..."
  }},
  "improvement_suggestions": [
    "具体修改建议1",
    "具体修改建议2",
    "具体修改建议3",
    ...
  ]
}}
"""

        # 构建上下文信息
        context_info = ""
        if context:
            if "previous_chapters" in context:
                context_info += "前面章节摘要:\n"
                for chapter in context["previous_chapters"][-2:]:  # 只取最近2章
                    context_info += f"- {chapter.get('title', '')}: {chapter.get('content', '')[:100]}...\n"

            if "character_profiles" in context:
                context_info += "\n人物设定:\n"
                context_info += self._character_profiles_to_text(context["character_profiles"])[:500] + "...\n"

            if "world_setting" in context:
                context_info += "\n世界观设定:\n"
                context_info += self._world_setting_to_text(context["world_setting"])[:300] + "...\n"

        prompt = await self._generate_prompt(prompt_template, {
            "chapter_content": chapter_content,
            "context_info": context_info
        })

        # 调用LLM评估章节
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
                        "情节连贯性": 0,
                        "人物一致性": 0,
                        "文笔质量": 0,
                        "节奏把控": 0,
                        "情感渲染": 0
                    },
                    "total_score": 0,
                    "evaluation_reasons": {
                        "error": "无法解析评估结果"
                    },
                    "improvement_suggestions": [
                        "无法提供具体建议，请检查输入内容"
                    ]
                }
        except Exception as e:
            # 如果JSON解析失败，返回错误信息
            return {
                "dimension_scores": {
                    "情节连贯性": 0,
                    "人物一致性": 0,
                    "文笔质量": 0,
                    "节奏把控": 0,
                    "情感渲染": 0
                },
                "total_score": 0,
                "evaluation_reasons": {
                    "error": f"解析评估结果时出错: {str(e)}"
                },
                "improvement_suggestions": [
                    "无法提供具体建议，请检查输入内容"
                ]
            }

    def _calculate_detailed_metrics(self, result: Dict, content_type: str) -> Dict[str, Any]:
        """
        计算详细的量化指标

        Args:
            result: 评估结果
            content_type: 内容类型

        Returns:
            Dict[str, Any]: 详细指标
        """
        dimension_scores = result.get("dimension_scores", {})
        total_score = result.get("total_score", 0)

        # 计算各维度的权重分布
        if dimension_scores:
            max_score = max(dimension_scores.values()) if dimension_scores.values() else 0
            min_score = min(dimension_scores.values()) if dimension_scores.values() else 0
            avg_score = sum(dimension_scores.values()) / len(dimension_scores) if dimension_scores else 0

            # 计算分数分布
            score_distribution = {
                "excellent": len([s for s in dimension_scores.values() if s >= 90]),
                "good": len([s for s in dimension_scores.values() if 80 <= s < 90]),
                "average": len([s for s in dimension_scores.values() if 70 <= s < 80]),
                "poor": len([s for s in dimension_scores.values() if s < 70])
            }

            # 计算质量等级
            if total_score >= 90:
                quality_grade = "优秀"
            elif total_score >= 80:
                quality_grade = "良好"
            elif total_score >= 70:
                quality_grade = "合格"
            else:
                quality_grade = "需要改进"

            return {
                "max_dimension_score": max_score,
                "min_dimension_score": min_score,
                "avg_dimension_score": round(avg_score, 2),
                "score_distribution": score_distribution,
                "quality_grade": quality_grade,
                "improvement_priority": min(dimension_scores, key=dimension_scores.get) if dimension_scores else "无",
                "strength_area": max(dimension_scores, key=dimension_scores.get) if dimension_scores else "无"
            }
        else:
            return {
                "max_dimension_score": 0,
                "min_dimension_score": 0,
                "avg_dimension_score": 0,
                "score_distribution": {"excellent": 0, "good": 0, "average": 0, "poor": 0},
                "quality_grade": "评估失败",
                "improvement_priority": "无",
                "strength_area": "无"
            }
