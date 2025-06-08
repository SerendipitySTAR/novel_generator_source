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

        **重要总体要求：** 在描述以下各个方面时，请始终思考它们之间的**相互联系**。例如，历史如何影响了当前的政治派别？独特的地理特征如何塑造了当地文化和信仰？魔法或科技体系如何影响社会结构和经济？请在每个主要部分的描述末尾明确指出其与至少另外两个世界观方面的关联。

        每套世界观应包含以下结构化内容:
        
        1.  **基础设定**：宇宙结构、物理规则、时间流速等基本公理。请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。
        2.  **地理环境**：
            *   大陆、国家、重要城市、特殊区域、奇观、气候特征。
            *   **环境互动**：描述地理环境如何直接影响居民的生活方式、信仰或冲突。提供至少一个例子，说明特定地理特征（如险峻山脉、巨大森林、资源匮乏的沙漠、特殊天象等）如何成为故事中潜在的机遇、挑战或象征。
            *   **有故事潜力的特色动植物 (Distinctive Flora/Fauna with Story Potential)**：描述1-2种对当地生态或文化至关重要的独特植物或动物，它们可能具有特殊的药用价值、神话意义，或者是重要的资源或危险源。
            *   请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。
        3.  **历史背景与传说**：
            *   **关键历史时期**：列出几个对当前世界格局有重大影响的关键历史时期及其标志性事件。
            *   **传说与神话**：讲述至少一个在本世界中广为流传的传说或神话故事，并解释这个故事如何影响当前人们的信仰、价值观或社会习俗。
            *   **被遗忘或争议的历史**：提及一两段可能被主流历史所忽略、遗忘或存在争议的历史片段或解读，这些片段可能在故事后续中变得重要或揭示某些真相。
            *   请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。
        4.  **主要势力/组织**：名称、标志、理念、领袖、核心成员、实力评估、控制区域、外交关系（同盟、敌对）。请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。
        5.  **能量体系/科技水平**：如魔法体系（元素、派系、施法条件、禁忌）、科技树（关键技术、发展水平、社会影响）。请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。
        6.  **文化与社会**：
            *   主要种族及其特征、语言体系。
            *   **社会结构**：阶级划分、权力结构、主要社会矛盾或冲突点。
            *   **核心价值观与信仰体系 (Main Beliefs/Pantheon)**：主流的价值观念。如果存在神系或主要宗教，描述其核心教义、主要神祇（及其领域、象征、仪式）、组织形式及其在社会中的影响力。包括创世神话或核心宇宙观。
            *   **文化习俗与艺术**：描述独特的文化习俗，例如，独特的节日、成人仪式、婚姻制度、丧葬习俗、社交礼仪、以及具有代表性的艺术形式（音乐、舞蹈、雕塑、绘画等）或娱乐活动。
            *   **主要经济活动与资源 (Main Economic Activities & Resources)**：描述支撑社会运作的主要经济活动（如农业、商业、手工业、开采业等）和关键资源（如矿产、特产、能源等）。
            *   请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。
        7.  **特殊生物/物种**：名称、习性、能力、与主要种族/人类的关系（如共生、敌对、被奴役、被崇拜等），以及它们在生态系统或文化中的独特角色。请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。
        8.  **核心世界魅力点 (Core World 'Wow Factors')**: 描述2-3个使这个世界真正独特且令人难忘的方面。这些可以是独特的自然现象、原创的社会结构、引人入胜的谜团、令人叹为观止的地点，或根深蒂固的文化怪癖。解释为什么这些元素具有吸引力，以及它们可能为故事带来的潜力。

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

        ## 核心世界魅力点 (Core World 'Wow Factors')
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
            world_setting_data = {
                "description": description,
                "sections": sections,
                "core_wow_factors": "" # Initialize new key
            }

            # Specifically parse "核心世界魅力点" if it exists as a top-level section
            if "核心世界魅力点 (Core World 'Wow Factors')" in sections:
                 world_setting_data["core_wow_factors"] = sections.pop("核心世界魅力点 (Core World 'Wow Factors')")
            elif "核心世界魅力点" in sections: # Fallback if the English part is missing
                 world_setting_data["core_wow_factors"] = sections.pop("核心世界魅力点")
            
            world_settings.append(world_setting_data)
        
        return world_settings
