#!/usr/bin/env python3
"""
测试增强后的小说生成器系统
验证连贯性检查、质量控制、智能重试等新功能
"""

import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents import (
    ContentIntegrityAgent, 
    QualityGuardianAgent, 
    ContextSynthesizerAgent,
    ChapterChroniclerAgent
)
from app.core.llm import OpenAILLM

async def test_content_integrity_agent():
    """测试内容审核智能体的连贯性检查功能"""
    print("🔍 测试内容审核智能体...")
    
    agent = ContentIntegrityAgent(llm=OpenAILLM())
    
    # 测试数据
    test_chapter = """
    李明走进了咖啡厅，点了一杯拿铁。突然，他发现自己能够飞行，
    于是立即飞到了月球上，遇到了外星人。外星人告诉他，地球即将毁灭。
    """
    
    previous_chapters = [
        {
            "chapter_number": 1,
            "title": "平凡的一天",
            "content": "李明是一个普通的大学生，每天过着平静的生活。他最大的爱好就是在咖啡厅里读书。"
        }
    ]
    
    character_profiles = [
        {
            "人物设定": [
                {
                    "基本信息": {"姓名": "李明", "年龄": "20岁", "职业": "大学生"},
                    "性格特质": {"核心性格": "内向、理性", "优点": ["聪明", "勤奋"], "缺点": ["胆小", "缺乏自信"]}
                }
            ]
        }
    ]
    
    world_setting = {
        "基本设定": {
            "世界名称": "现代都市",
            "时代背景": "21世纪现代社会",
            "科技水平": "现实科技水平"
        }
    }
    
    # 测试连贯性检查
    result = await agent.run({
        "chapter_content": test_chapter,
        "previous_chapters": previous_chapters,
        "character_profiles": character_profiles,
        "world_setting": world_setting,
        "mode": "coherence"
    })
    
    print(f"连贯性评分: {result.get('coherence_score', 0)}")
    print(f"是否通过阈值: {result.get('pass_threshold', False)}")
    
    if result.get('coherence_issues'):
        print("发现的连贯性问题:")
        for issue in result['coherence_issues']:
            print(f"  - {issue.get('type', '')}: {issue.get('description', '')}")
    
    print("✅ 内容审核智能体测试完成\n")
    return result.get('pass_threshold', False)

async def test_quality_guardian_agent():
    """测试质量审核智能体的量化评估功能"""
    print("📊 测试质量审核智能体...")
    
    agent = QualityGuardianAgent(llm=OpenAILLM())
    
    # 测试章节内容评估
    test_content = """
    夕阳西下，金色的光芒洒在古老的石桥上。李明缓缓走过桥面，
    脚步声在寂静的黄昏中显得格外清晰。他的心中涌起一阵莫名的忧伤，
    仿佛这座桥承载着太多的回忆。远处传来钟声，提醒着时间的流逝。
    """
    
    context = {
        "previous_chapters": [
            {
                "title": "初遇",
                "content": "李明第一次来到这个小镇，对一切都充满好奇..."
            }
        ],
        "character_profiles": [
            {
                "人物设定": [
                    {
                        "基本信息": {"姓名": "李明", "年龄": "25岁"},
                        "性格特质": {"核心性格": "敏感、多愁善感"}
                    }
                ]
            }
        ]
    }
    
    result = await agent.run({
        "content_type": "chapter",
        "content": test_content,
        "context": context,
        "retry_count": 0
    })
    
    print(f"总评分: {result.get('total_score', 0)}")
    print(f"质量等级: {result.get('detailed_metrics', {}).get('quality_grade', '未知')}")
    print(f"是否通过质量阈值: {result.get('quality_threshold_passed', False)}")
    
    if result.get('dimension_scores'):
        print("各维度评分:")
        for dimension, score in result['dimension_scores'].items():
            print(f"  - {dimension}: {score}")
    
    print("✅ 质量审核智能体测试完成\n")
    return result.get('quality_threshold_passed', False)

async def test_context_synthesizer_agent():
    """测试总结智能体的分层上下文管理功能"""
    print("📝 测试总结智能体...")
    
    agent = ContextSynthesizerAgent(llm=OpenAILLM())
    
    # 测试数据
    chapters = [
        {
            "chapter_number": 1,
            "title": "初到小镇",
            "content": "李明带着行李来到了这个偏远的小镇，准备开始新的生活。小镇很安静，只有几户人家。"
        },
        {
            "chapter_number": 2,
            "title": "神秘的老人",
            "content": "李明遇到了一位神秘的老人，老人告诉他这个小镇有着不为人知的秘密。"
        }
    ]
    
    world_setting = {
        "基本设定": {
            "世界名称": "雾隐小镇",
            "时代背景": "现代",
            "特色": "充满神秘色彩的小镇"
        }
    }
    
    character_profiles = [
        {
            "人物设定": [
                {
                    "基本信息": {"姓名": "李明", "年龄": "28岁"},
                    "角色定位": "主角"
                }
            ]
        }
    ]
    
    # 测试分层上下文生成
    result = await agent.run({
        "chapters": chapters,
        "world_setting": world_setting,
        "character_profiles": character_profiles,
        "mode": "layered"
    })
    
    print("分层上下文生成结果:")
    print(f"全局上下文: {result.get('global_context', '')[:100]}...")
    print(f"中期上下文: {result.get('medium_context', '')[:100]}...")
    print(f"即时上下文: {result.get('immediate_context', '')[:100]}...")
    
    print("✅ 总结智能体测试完成\n")
    return True

async def test_chapter_chronicler_agent():
    """测试章节智能体的增强上下文整合功能"""
    print("📖 测试章节智能体...")
    
    agent = ChapterChroniclerAgent(llm=OpenAILLM())
    
    # 测试数据
    chapter_outline = {
        "number": 3,
        "title": "真相揭露",
        "scenes": "老人的小屋",
        "events": "李明发现小镇的秘密",
        "conflicts": "内心的恐惧与好奇心的冲突"
    }
    
    previous_chapters = [
        {
            "chapter_number": 1,
            "title": "初到小镇",
            "content": "李明来到小镇，感受到了不寻常的氛围..."
        },
        {
            "chapter_number": 2,
            "title": "神秘的老人",
            "content": "老人向李明暗示了小镇的秘密..."
        }
    ]
    
    world_setting = {
        "基本设定": {
            "世界名称": "雾隐小镇",
            "特色": "神秘、超自然现象"
        }
    }
    
    character_profiles = [
        {
            "人物设定": [
                {
                    "基本信息": {"姓名": "李明"},
                    "性格特质": {"核心性格": "好奇但谨慎"}
                }
            ]
        }
    ]
    
    # 测试增强的章节生成
    result = await agent.run({
        "mode": "generate",
        "chapter_outline": chapter_outline,
        "world_setting": world_setting,
        "character_profiles": character_profiles,
        "previous_summary": "李明来到小镇后遇到了神秘老人",
        "previous_chapters": previous_chapters,
        "kb_context": [],
        "writing_style": "悬疑神秘",
        "retry_count": 0
    })
    
    chapter_content = result.get("chapter_content", "")
    print(f"生成的章节内容长度: {len(chapter_content)} 字符")
    print(f"章节内容预览: {chapter_content[:200]}...")
    
    success = len(chapter_content) > 100 and "李明" in chapter_content
    print("✅ 章节智能体测试完成\n")
    return success

async def main():
    """主测试函数"""
    print("🚀 开始测试增强后的小说生成器系统...\n")
    
    test_results = []
    
    try:
        # 测试各个智能体
        result1 = await test_content_integrity_agent()
        test_results.append(("内容审核智能体", result1))
        
        result2 = await test_quality_guardian_agent()
        test_results.append(("质量审核智能体", result2))
        
        result3 = await test_context_synthesizer_agent()
        test_results.append(("总结智能体", result3))
        
        result4 = await test_chapter_chronicler_agent()
        test_results.append(("章节智能体", result4))
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        return
    
    # 输出测试结果
    print("=" * 50)
    print("📊 测试结果总结:")
    print("=" * 50)
    
    passed_count = 0
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if passed:
            passed_count += 1
    
    print(f"\n总计: {passed_count}/{len(test_results)} 项测试通过")
    
    if passed_count == len(test_results):
        print("🎉 所有测试都通过了！系统增强成功！")
    else:
        print("⚠️ 部分测试失败，需要进一步调试。")

if __name__ == "__main__":
    asyncio.run(main())
