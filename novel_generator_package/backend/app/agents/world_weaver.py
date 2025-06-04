"""
世界观智能体 (World Weaver Agent)
负责生成详细、完整且结构化的世界观设定
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.core.llm import LLMInterface, LLMResponse
from app.core.knowledge_base import KnowledgeBase
from app.config import settings

class WorldWeaverAgent(BaseAgent):
    """世界观智能体，负责生成世界观设定"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行世界观智能体

        Args:
            input_data: 输入数据，包含:
                - narrative_concept: 用户选定/编辑后的小说概述
                - num_settings: 需要生成的世界观设定数量

        Returns:
            Dict[str, Any]: 输出数据，包含:
                - world_settings: 生成的世界观设定列表
        """
        narrative_concept = input_data.get("narrative_concept", "")
        num_settings = input_data.get("num_settings", 3)

        print(f"世界观智能体：开始运行，概述长度: {len(narrative_concept)}, 生成数量: {num_settings}")
        
        # 构建提示词
        prompt_template = """
        你是一位资深世界构建师。基于以下小说概述，请构建{num_settings}套详细、自洽且结构化的世界观。

        每套世界观应包含以下结构化内容:
        
        1. 基础设定：宇宙结构、物理规则、时间流速等。
        2. 地理环境：大陆、国家、重要城市、特殊区域、奇观、气候特征。
        3. 历史背景：重大历史事件年表、传说、神话。
        4. 主要势力/组织：名称、标志、理念、领袖、核心成员、实力评估、控制区域、外交关系（同盟、敌对）。
        5. 能量体系/科技水平：如魔法体系（元素、派系、施法条件、禁忌）、科技树（关键技术、发展水平、社会影响）。
        6. 文化与社会：种族、语言、宗教信仰、社会结构、价值观念、艺术风格、风俗习惯。
        7. 特殊生物/物种：名称、习性、能力、与人类关系。
        
        请确保世界观的每一项设定都能支撑概述中的核心情节，并预留扩展空间。每套世界观应该有其独特的特点和魅力，但都要与小说概述相契合。
        
        小说概述:
        {narrative_concept}
        
        请按照以下格式输出，为每套世界观添加编号和简短的特色描述:
        
        # 世界观1：[简短特色描述]
        
        ## 基础设定
        [详细内容]
        
        ## 地理环境
        [详细内容]
        
        ## 历史背景
        [详细内容]
        
        ## 主要势力/组织
        [详细内容]
        
        ## 能量体系/科技水平
        [详细内容]
        
        ## 文化与社会
        [详细内容]
        
        ## 特殊生物/物种
        [详细内容]
        
        # 世界观2：[简短特色描述]
        
        ...以此类推
        """
        
        prompt = await self._generate_prompt(prompt_template, {
            "num_settings": num_settings,
            "narrative_concept": narrative_concept
        })

        print(f"世界观智能体：生成的提示词长度: {len(prompt)}")

        # 调用LLM生成世界观设定
        print("世界观智能体：开始调用LLM")
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=0.7,
            max_tokens=settings.WORLD_SETTING_MAX_TOKENS,
            top_p=0.9
        )

        print(f"世界观智能体：LLM响应长度: {len(response.text)}")

        # 解析响应，提取世界观设定
        world_settings = self._parse_world_settings(response.text)

        print(f"世界观智能体：解析出 {len(world_settings)} 个世界观设定")

        return {
            "world_settings": world_settings
        }
    
    def _parse_world_settings(self, text: str) -> List[Dict[str, Any]]:
        """
        从LLM响应中解析出世界观设定列表
        
        Args:
            text: LLM响应文本
            
        Returns:
            List[Dict[str, Any]]: 世界观设定列表
        """
        world_settings = []
        
        # 按"# 世界观"分割
        settings_texts = text.split("# 世界观")
        
        # 跳过第一个空部分（如果存在）
        for setting_text in settings_texts[1:]:
            if not setting_text.strip():
                continue

            # 提取特色描述
            lines = setting_text.split("\n")
            title_line = lines[0].strip()
            description = ""

            # 提取特色描述（如果存在）
            if "：" in title_line or ":" in title_line:
                title_parts = title_line.replace("：", ":").split(":", 1)
                if len(title_parts) > 1:
                    description = title_parts[1].strip()

            # 解析各部分内容 - 使用完整的setting_text而不是被分割的部分
            content = setting_text
            sections = {}
            
            # 提取各部分内容
            current_section = None
            current_content = []
            
            for line in content.split("\n"):
                if line.startswith("## "):
                    # 保存上一部分内容
                    if current_section:
                        sections[current_section] = "\n".join(current_content).strip()
                    
                    # 开始新部分
                    current_section = line[3:].strip()
                    current_content = []
                elif current_section:
                    current_content.append(line)
            
            # 保存最后一部分内容
            if current_section:
                sections[current_section] = "\n".join(current_content).strip()
            
            # 构建结构化的世界观设定
            world_setting = {
                "description": description,
                "sections": sections
            }
            
            world_settings.append(world_setting)
        
        return world_settings
