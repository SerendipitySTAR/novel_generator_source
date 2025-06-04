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
1. 保持原始内容的核心情节和信息不变
2. 提升语言的文学性和表现力
3. 优化句式结构，使其更加流畅自然
4. 增强{focus_areas_text}的表现力
5. 确保符合{style}风格的特点

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
