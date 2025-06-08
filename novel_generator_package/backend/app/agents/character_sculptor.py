"""
人物刻画智能体，负责生成详细的主要人物设定
"""
from typing import Dict, List, Optional, Any, Union
from app.agents.base_agent import BaseAgent
from app.config import settings

class CharacterSculptorAgent(BaseAgent):
    """人物刻画智能体"""
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行人物刻画智能体
        
        Args:
            input_data: 输入数据，包含：
                - narrative_concept: 小说概述
                - world_setting: 世界观设定
                - plot_outline: 大纲
                - num_profiles: 生成人物设定集的数量，默认为2
            
        Returns:
            Dict[str, Any]: 输出数据，包含：
                - character_profiles: 生成的主要人物设定集列表
        """
        narrative_concept = input_data.get("narrative_concept", "")
        world_setting = input_data.get("world_setting", {})
        plot_outline = input_data.get("plot_outline", {})
        num_profiles = input_data.get("num_profiles", 2)
        
        # 将世界观设定转换为文本
        world_setting_text = self._world_setting_to_text(world_setting)
        
        # 从大纲中提取人物名称
        character_names = self._extract_character_names(plot_outline)
        
        # 构建提示词
        prompt_template = """你是一位洞察人性的角色设计师。根据以下小说概述、世界观和大纲，请为主要人物创建{num_profiles}套详细设定。每套设定中，每个角色应包含以下内容：

1. 基本信息：姓名、性别、年龄、种族、外貌特征、衣着风格。
2. 详细背景故事 (Detailed Backstory):
    a. **关键童年/成长经历 (Key Childhood/Formative Experience):** 描述1-2个对其性格和价值观形成至关重要的童年或成长事件。
    b. **重大人生转折点 (Major Life Turning Point):** 描述一个彻底改变其人生轨迹的事件，或一个重大的成就/失败。
    c. **核心秘密/未解之谜 (Core Secret/Unresolved Mystery):** 设定一个与其背景相关的秘密，或一个可能在未来情节中揭示的未解之谜。
    d. **背景故事与潜在情节钩子 (Backstory & Potential Plot Hooks):** 简要说明这些背景元素如何可能成为未来情节的引爆点或提供角色发展的机会。
3. 性格特质：核心性格、价值观、优点。对于主要**缺点 (Flaws/Shortcomings)**，请思考它们如何不仅仅是性格缺陷，也可能是在特定情境下会制造麻烦或情节冲突的具体短板；简述其可能如何引发冲突或使角色陷入困境。其他可包含：癖好、口头禅。
4. 能力技能：掌握的技能、知识、特殊能力（需符合世界观设定）、力量等级（如适用）。请确保这些技能与小说的主题、世界观或预期冲突类型相关。为每项主要技能简述其在故事中可能的应用场景或如何帮助角色克服挑战。
5. 内在景观 (Internal Landscape):
    a. 动机与目标：内心深层驱动力、在故事中的短期/长期目标。
    b. 内在冲突与困境：角色面临的主要内部矛盾、道德困境或价值观冲突，这些冲突如何影响其决策？
    c. 深层动机与潜意识：角色可能未完全意识到的恐惧、渴望或过去经历的创伤，这些潜意识因素如何隐秘地影响其行为？
6. 角色弧光：预期的性格转变、成长轨迹（如从懦弱到勇敢，从迷茫到坚定）。关键的成长契机是什么？
7. 人际关系与动态演变 (Relationship Dynamics and Evolution):
    a. 与其他主要人物的初步关系设定（亲友、敌人、爱慕对象、竞争对手等）。
    b. 关系演变潜力：思考这些关键关系在故事发展中可能如何变化（例如，盟友可能因背叛成为敌人，竞争对手可能在共同危机中成为伙伴）。列出1-2种最可能的关系演变路径及其触发条件。

小说概述:
{narrative_concept}

世界观:
{world_setting_text}

大纲:
{plot_outline_text}

需要设计的主要人物:
{character_names}

请着重刻画角色的内在动机、潜在冲突以及预期的角色发展弧光。思考并简述他们之间可能形成的人物关系。请按照以下JSON格式输出{num_profiles}套不同的人物设定，每套设定之间用"====="分隔:

{{
  "人物设定": [
    {{
      "基本信息": {{
        "姓名": "...",
        "性别": "...",
        "年龄": "...",
        "种族": "...",
        "外貌特征": ["...", "..."],
        "衣着风格": "..."
      }},
      "背景故事": {{
        "关键童年经历": "...",
        "重大人生转折点": "...",
        "核心秘密": "...",
        "情节钩子": "..."
      }},
      "性格特质": {{
        "核心性格": "...",
        "价值观": "...",
        "优点": ["...", "..."],
        "缺点": [
          {{"缺陷": "过度自信", "情节关联": "可能导致其在关键时刻低估敌人，造成失败。"}},
          "..."
        ],
        "癖好": "...",
        "口头禅": "..."
      }},
      "能力技能": {{
        "技能": [
          {{"技能名称": "精准射击", "描述": "百步穿杨的弓箭手。", "情节关联": "在远程战斗或需要精确操作的场合发挥关键作用，例如射中远处的机关。"}},
          "..."
        ],
        "知识": ["...", "..."],
        "特殊能力": "...",
        "力量等级": "..."
      }},
      "内在景观": {{
        "动机与目标": {{
          "内心驱动力": "...",
          "短期目标": "...",
          "长期目标": "..."
        }},
        "内在冲突与困境": "...",
        "深层动机与潜意识": "..."
      }},
      "角色弧光": "...",
      "人际关系与动态演变": {{
        "初始关系": [
          {{"关系对象": "人物2", "关系类型": "...", "关系描述": "..."}},
          {{"关系对象": "人物3", "关系类型": "...", "关系描述": "..."}}
        ],
        "关系演变潜力": [
          {{"关系对象": "人物2", "演变路径": "...", "触发条件": "..."}}
        ]
      }}
    }},
    {{
      "基本信息": {{
        "姓名": "...",
        "性别": "...",
        "年龄": "...",
        "种族": "...",
        "外貌特征": ["...", "..."],
        "衣着风格": "..."
      }},
      "背景故事": {{
        "关键童年经历": "...",
        "重大人生转折点": "...",
        "核心秘密": "...",
        "情节钩子": "..."
      }},
      "性格特质": {{
        "核心性格": "...",
        "价值观": "...",
        "优点": ["...", "..."],
        "缺点": [
           {{"缺陷": "优柔寡断", "情节关联": "在紧急抉择时可能错失良机，或给同伴带来危险。"}},
           "..."
        ],
        "癖好": "...",
        "口头禅": "..."
      }},
      "能力技能": {{
        "技能": [
          {{"技能名称": "古代文献解读", "描述": "能解读失落文明的文字。", "情节关联": "帮助团队解开古老谜题，找到关键线索。"}},
          "..."
        ],
        "知识": ["...", "..."],
        "特殊能力": "...",
        "力量等级": "..."
      }},
      "内在景观": {{
        "动机与目标": {{
          "内心驱动力": "...",
          "短期目标": "...",
          "长期目标": "..."
        }},
        "内在冲突与困境": "...",
        "深层动机与潜意识": "..."
      }},
      "角色弧光": "...",
      "人际关系与动态演变": {{
        "初始关系": [
          {{"关系对象": "人物1", "关系类型": "...", "关系描述": "..."}},
          {{"关系对象": "人物3", "关系类型": "...", "关系描述": "..."}}
        ],
        "关系演变潜力": [
          {{"关系对象": "人物1", "演变路径": "...", "触发条件": "..."}}
        ]
      }}
      ]
    }},
    ...
  ],
  "人物关系图谱": "简要描述主要人物之间的关系网络"
}}

=====

...
"""
        
        # 将大纲转换为文本
        plot_outline_text = self._plot_outline_to_text(plot_outline)
        
        # 将人物名称列表转换为文本
        character_names_text = "\n".join([f"- {name}" for name in character_names])
        
        prompt = await self._generate_prompt(prompt_template, {
            "narrative_concept": narrative_concept,
            "world_setting_text": world_setting_text,
            "plot_outline_text": plot_outline_text,
            "character_names": character_names_text,
            "num_profiles": num_profiles
        })
        
        # 调用LLM生成人物设定
        response = await self.llm.generate_text(
            prompt=prompt,
            temperature=settings.AGENT_TEMPERATURE,
            max_tokens=settings.CHARACTER_MAX_TOKENS,
            top_p=settings.AGENT_TOP_P
        )
        
        # 解析结果
        character_profiles = []
        raw_profiles = response.text.split("=====")
        
        import json
        import re
        
        for profile in raw_profiles:
            profile = profile.strip()
            if profile:
                try:
                    # 使用正则表达式提取JSON部分
                    json_match = re.search(r'\{.*\}', profile, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        # 解析JSON
                        character_profile = json.loads(json_str)
                        character_profiles.append(character_profile)
                except Exception as e:
                    # 如果JSON解析失败，将原始文本作为非结构化数据添加
                    character_profiles.append({"raw_text": profile})
        
        return {"character_profiles": character_profiles}
    
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
        
        # 文化与社会
        if "文化与社会" in world_setting:
            text += "【文化与社会】\n"
            for key, value in world_setting["文化与社会"].items():
                if isinstance(value, list):
                    text += f"- {key}: {', '.join(value)}\n"
                else:
                    text += f"- {key}: {value}\n"
            text += "\n"
        
        # 能量体系/科技水平
        if "能量体系/科技水平" in world_setting:
            text += "【能量体系/科技水平】\n"
            text += f"- 类型: {world_setting['能量体系/科技水平'].get('类型', '')}\n"
            text += f"- 详细描述: {world_setting['能量体系/科技水平'].get('详细描述', '')}\n"
            
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
    
    def _extract_character_names(self, plot_outline: Dict[str, Any]) -> List[str]:
        """
        从大纲中提取人物名称
        
        Args:
            plot_outline: 大纲
            
        Returns:
            List[str]: 人物名称列表
        """
        character_names = set()
        
        # 如果是原始文本，返回空列表
        if "raw_text" in plot_outline:
            return []
        
        # 从章节列表中提取
        if "章节列表" in plot_outline and isinstance(plot_outline["章节列表"], list):
            for chapter in plot_outline["章节列表"]:
                if "核心内容" in chapter and "出场人物" in chapter["核心内容"]:
                    for character in chapter["核心内容"]["出场人物"]:
                        character_names.add(character)
        
        # 从多线叙事中提取
        if "多线叙事" in plot_outline and isinstance(plot_outline["多线叙事"], list):
            for storyline in plot_outline["多线叙事"]:
                if "主要人物" in storyline:
                    for character in storyline["主要人物"]:
                        character_names.add(character)
        
        return list(character_names)
