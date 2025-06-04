#!/usr/bin/env python3
"""
测试章节生成和人物设定修复的脚本
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.chapter_chronicler import ChapterChroniclerAgent
from app.core.llm import OpenAILLM

async def test_chapter_generation():
    """测试章节生成功能"""
    print("=" * 50)
    print("测试章节生成功能")
    print("=" * 50)
    
    try:
        # 创建章节智能体
        agent = ChapterChroniclerAgent(llm=OpenAILLM(), project_id="test_project")
        
        # 测试数据
        test_data = {
            "mode": "generate",
            "chapter_outline": {
                "number": 1,
                "title": "第一章：初遇",
                "scenes": "主角在图书馆遇到神秘女子",
                "events": "主角发现古老的魔法书籍",
                "conflicts": "主角内心的困惑与好奇",
                "turning_points": "魔法书籍突然发光",
                "emotional_tone": "神秘、好奇",
                "foreshadowing": "暗示主角的特殊身份",
                "characters": "主角李明，神秘女子艾莉",
                "word_count": "2000-3000"
            },
            "world_setting": {
                "background": "现代都市中隐藏着魔法世界",
                "magic_system": "通过古老书籍激活魔法",
                "locations": "市立图书馆、隐秘的魔法区域"
            },
            "character_profiles": [{
                "name": "李明",
                "age": 22,
                "personality": "好奇心强，善于思考",
                "background": "大学生，对神秘事物感兴趣"
            }],
            "previous_summary": "",
            "kb_context": [],
            "writing_style": "细腻生动，富有想象力"
        }
        
        print("开始生成章节...")
        result = await agent.run(test_data)
        
        print(f"生成结果类型: {type(result)}")
        print(f"生成结果键: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and "chapter_content" in result:
            chapter_content = result["chapter_content"]
            print(f"章节内容长度: {len(chapter_content)}")
            print(f"章节内容预览: {chapter_content[:200]}...")
            
            if chapter_content and chapter_content.strip():
                print("✅ 章节生成成功！")
                return True
            else:
                print("❌ 章节内容为空！")
                return False
        else:
            print(f"❌ 返回结果格式错误: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 章节生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_character_name_extraction():
    """测试人物名字提取功能"""
    print("\n" + "=" * 50)
    print("测试人物名字提取功能")
    print("=" * 50)
    
    # 测试数据
    test_cases = [
        {
            "name": "字符串格式",
            "content": "姓名：张三\n年龄：25\n职业：程序员",
            "expected": ["张三"]
        },
        {
            "name": "结构化格式（中文）",
            "content": {
                "人物设定": [
                    {"基本信息": {"姓名": "李四", "年龄": 30}},
                    {"基本信息": {"姓名": "王五", "年龄": 28}}
                ]
            },
            "expected": ["李四", "王五"]
        },
        {
            "name": "结构化格式（英文）",
            "content": {
                "characters": [
                    {"name": "Alice", "age": 25},
                    {"basic_info": {"name": "Bob", "age": 30}}
                ]
            },
            "expected": ["Alice", "Bob"]
        }
    ]
    
    # 模拟人物名字提取函数
    def get_character_names(character_data):
        content = character_data.get("content") if isinstance(character_data, dict) else character_data
        if not content:
            return ['未命名角色']

        # 如果content是字符串，尝试从中提取姓名
        if isinstance(content, str):
            import re
            name_match = re.search(r'(?:姓名|名字|Name)[：:]\s*([^\s,，。\n]+)', content)
            if name_match:
                return [name_match.group(1)]
            return ['未命名角色']

        # 如果content有characters数组
        if isinstance(content, dict) and content.get("characters") and isinstance(content["characters"], list):
            names = []
            for i, char in enumerate(content["characters"]):
                if isinstance(char, dict):
                    if char.get("name"):
                        names.append(char["name"])
                    elif char.get("basic_info", {}).get("name"):
                        names.append(char["basic_info"]["name"])
                    else:
                        names.append(f"角色{i + 1}")
                else:
                    names.append(f"角色{i + 1}")
            return names

        # 如果content有人物设定字段
        if isinstance(content, dict) and content.get("人物设定") and isinstance(content["人物设定"], list):
            names = []
            for i, char in enumerate(content["人物设定"]):
                if isinstance(char, dict):
                    if char.get("基本信息", {}).get("姓名"):
                        names.append(char["基本信息"]["姓名"])
                    elif char.get("name"):
                        names.append(char["name"])
                    else:
                        names.append(f"角色{i + 1}")
                else:
                    names.append(f"角色{i + 1}")
            return names

        return ['未命名角色']
    
    success_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        print(f"\n测试用例: {test_case['name']}")
        character_data = {"content": test_case["content"]}
        result = get_character_names(character_data)
        expected = test_case["expected"]
        
        print(f"期望结果: {expected}")
        print(f"实际结果: {result}")
        
        if result == expected:
            print("✅ 测试通过")
            success_count += 1
        else:
            print("❌ 测试失败")
    
    print(f"\n人物名字提取测试结果: {success_count}/{total_count} 通过")
    return success_count == total_count

async def main():
    """主测试函数"""
    print("开始测试章节生成和人物设定修复...")
    
    # 测试章节生成
    chapter_test_passed = await test_chapter_generation()
    
    # 测试人物名字提取
    character_test_passed = test_character_name_extraction()
    
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"章节生成测试: {'✅ 通过' if chapter_test_passed else '❌ 失败'}")
    print(f"人物名字提取测试: {'✅ 通过' if character_test_passed else '❌ 失败'}")
    
    if chapter_test_passed and character_test_passed:
        print("\n🎉 所有测试都通过了！修复成功！")
        return True
    else:
        print("\n⚠️ 部分测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    asyncio.run(main())
