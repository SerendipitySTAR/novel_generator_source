"""
润色智能体，负责对生成的小说内容进行润色和优化
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class StylePolisherAgent(BaseAgent):
    """润色智能体"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行润色智能体
        
        Args:
            input_data: 输入数据，包含：
                - content: 需要润色的内容
                - style: 目标风格
                - focus_areas: 重点关注的方面，如"描写"、"对话"、"情感"等
            
        Returns:
            Dict[str, Any]: 输出数据，包含：
                - polished_content: 润色后的内容
                - changes_summary: 修改摘要
        """
        content = input_data.get("content", "")
        style = input_data.get("style", "")
        focus_areas = input_data.get("focus_areas", [])
        
        # 构建提示词
        prompt_template = """你是一位文学润色大师，擅长将普通文本提升为优美的文学作品。请对以下内容进行润色，使其符合{style}风格，并重点优化以下方面：{focus_areas_text}。

原始内容:
{content}

请按照以下要求进行润色：
1. 核心保留：保持原始内容的核心情节、人物关系和关键信息不变。
2. 文学性提升：显著提升语言的文学性和表现力。
    *   **增强情感共鸣 (Emotional Resonance)**：仔细斟酌词语和句式，以增强文本的情感冲击力。例如，使用更具表现力的动词和形容词，根据场景的情感基调调整句子的长短和节奏。
    *   **运用文学手法 (Literary Devices)**：在适当之处，考虑融入隐喻（暗喻/比喻 Metaphors）、明喻 (Similes) 和象征 (Symbolism) 等文学手法，以丰富文本层次感和深层含义。这些手法应自然贴切，不显刻意。
3. 句式优化：优化句式结构，使其更加流畅、自然，并富于变化。
4. 突出重点：根据指定的重点关注方面（{focus_areas_text}），针对性地进行强化和提升。
5. 风格契合：
    *   确保整体风格符合 {style} 的要求。
    *   **特定风格模仿 (Specific Style Imitation)**：如果 {style} 指向特定的文学流派（如“经典哥特小说风格”）或作家（如“海明威风格”），请深入分析并模仿其关键特征，包括但不限于：常用词汇、典型句式、叙事节奏、常见意象或主题。若 {style} 为通用描述（如“生动形象”），则以提升整体文学质量为准。

请提供润色后的内容，以及一个简短的修改摘要，说明你做了哪些主要改进。
"""
        
        # 将重点关注的方面转换为文本
        focus_areas_text = "、".join(focus_areas) if focus_areas else "整体表达"
        
        prompt = await self._generate_prompt(prompt_template, {
            "content": content,
            "style": style,
            "focus_areas_text": focus_areas_text
        })
        
        # 调用LLM润色内容
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.7,  # 使用较高的温度以增加创造性
            max_tokens=settings.CHAPTER_POLISH_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )
        
        # 解析结果
        result_text = response.text
        
        # 尝试分离润色后的内容和修改摘要
        polished_content = result_text
        changes_summary = ""
        
        # 常见的分隔标记
        separators = ["修改摘要:", "修改摘要：", "修改总结:", "修改总结：", 
                     "修改说明:", "修改说明：", "改进摘要:", "改进摘要：",
                     "润色摘要:", "润色摘要：", "润色总结:", "润色总结："]
        
        for separator in separators:
            if separator in result_text:
                parts = result_text.split(separator, 1)
                polished_content = parts[0].strip()
                changes_summary = separator + parts[1].strip()
                break
        
        return {
            "polished_content": polished_content,
            "changes_summary": changes_summary
        }
