#!/usr/bin/env python3
"""
调试LLM响应和解析
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.world_weaver import WorldWeaverAgent
from app.core.llm import OpenAILLM

async def debug_llm_response():
    """调试LLM响应和解析"""
    print("开始调试LLM响应...")
    
    # 创建智能体
    llm = OpenAILLM()
    agent = WorldWeaverAgent(llm=llm)
    
    # 测试输入
    test_input = {
        "narrative_concept": "这是一个关于魔法世界的小说，主角是一个年轻的法师，他要拯救世界免受黑暗势力的侵害。",
        "num_settings": 2
    }
    
    print(f"输入概述: {test_input['narrative_concept']}")
    print(f"生成数量: {test_input['num_settings']}")
    print()
    
    # 生成提示词
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
    
    prompt = await agent._generate_prompt(prompt_template, {
        "num_settings": test_input["num_settings"],
        "narrative_concept": test_input["narrative_concept"]
    })
    
    print("生成的提示词:")
    print("=" * 50)
    print(prompt)
    print("=" * 50)
    print()
    
    # 调用LLM
    print("调用LLM...")
    response = await llm.generate_text(
        prompt=prompt,
        temperature=0.7,
        max_tokens=4000,
        top_p=0.9
    )
    
    print("LLM原始响应:")
    print("=" * 50)
    print(response.text)
    print("=" * 50)
    print()
    
    # 解析响应
    print("解析响应...")
    world_settings = agent._parse_world_settings(response.text)
    
    print(f"解析出 {len(world_settings)} 个世界观设定:")
    for i, setting in enumerate(world_settings):
        print(f"\n世界观 {i+1}:")
        print(f"  描述: {setting.get('description', 'N/A')}")
        print(f"  部分数量: {len(setting.get('sections', {}))}")
        if setting.get('sections'):
            print(f"  包含部分: {list(setting['sections'].keys())}")
            for section_name, section_content in setting['sections'].items():
                print(f"    {section_name}: {section_content[:100]}...")
        else:
            print("  警告：sections为空")

if __name__ == "__main__":
    asyncio.run(debug_llm_response())
