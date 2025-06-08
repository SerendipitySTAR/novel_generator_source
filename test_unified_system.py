#!/usr/bin/env python3
"""
测试统一数据库系统的完整功能
"""
import requests
import json
import time

def test_unified_system():
    """测试统一系统"""
    base_url = "http://localhost:8002/api"
    
    print("=== 测试统一数据库系统 ===")
    
    # 1. 创建项目
    print("\n1. 创建测试项目")
    project_data = {
        "title": "统一数据库测试项目",
        "description": "验证数据库统一后的完整功能"
    }
    
    response = requests.post(f"{base_url}/projects", json=project_data)
    if response.status_code != 200:
        print(f"❌ 项目创建失败: {response.status_code}")
        return False
    
    project = response.json()
    project_id = project["id"]
    print(f"✅ 项目创建成功: {project['title']} (ID: {project_id[:8]}...)")
    
    # 2. 创建概述
    print("\n2. 创建概述")
    concept_data = {
        "title": "测试概述",
        "content": """**核心概念**：
一个现代程序员意外穿越到修仙世界，发现修仙体系可以用编程思维优化。

**主要冲突**：
1. 现代科学思维与传统修仙理念的碰撞
2. 用代码逻辑优化修炼功法引发的宗门争议  
3. 发现修仙世界背后隐藏的"系统"真相

**故事亮点**：
- 用编程思维重新解构修仙体系
- 将修炼功法转化为可执行的"代码"
- 探索修仙世界的底层"操作系统" """
    }
    
    response = requests.post(f"{base_url}/projects/{project_id}/concepts", json=concept_data)
    if response.status_code != 200:
        print(f"❌ 概述创建失败: {response.status_code}")
        return False
    
    concept = response.json()
    concept_id = concept["id"]
    print(f"✅ 概述创建成功: {concept['title']}")
    
    # 选中概述
    response = requests.patch(f"{base_url}/projects/{project_id}/concepts/{concept_id}", 
                             json={"is_selected": True})
    if response.status_code == 200:
        print("✅ 概述已选中")
    
    # 3. 创建世界观
    print("\n3. 创建世界观")
    world_data = {
        "title": "修仙编程世界",
        "content": {
            "description": "一个修仙与编程融合的奇幻世界",
            "sections": {
                "基础设定": "修仙者通过'灵力编程'来施展法术，每个功法都是一段可执行的代码",
                "地理环境": "各大宗门如同不同的开发团队，拥有各自的编程语言和框架",
                "修炼体系": "从初级程序员（练气期）到架构师（元婴期）的完整修炼路径",
                "特殊规则": "修仙世界存在'天道编译器'，会检查和优化所有修炼者的'代码'"
            }
        }
    }
    
    response = requests.post(f"{base_url}/projects/{project_id}/world-settings", json=world_data)
    if response.status_code != 200:
        print(f"❌ 世界观创建失败: {response.status_code}")
        return False
    
    world_setting = response.json()
    world_id = world_setting["id"]
    print(f"✅ 世界观创建成功: {world_setting['title']}")
    
    # 选中世界观
    response = requests.patch(f"{base_url}/projects/{project_id}/world-settings/{world_id}", 
                             json={"is_selected": True})
    if response.status_code == 200:
        print("✅ 世界观已选中")
    
    # 4. 创建大纲
    print("\n4. 创建大纲")
    plot_data = {
        "title": "编程修仙大纲",
        "content": {
            "version": "1",
            "structure": "三幕式结构：觉醒-成长-超越",
            "chapters": [
                {"number": 1, "title": "代码觉醒", "word_count": 3000},
                {"number": 2, "title": "功法重构", "word_count": 3500},
                {"number": 3, "title": "系统升级", "word_count": 4000}
            ],
            "chapter_details": [
                {
                    "number": 1,
                    "title": "代码觉醒",
                    "scenes": "现代办公室，修仙世界入门宗门",
                    "characters": "主角李程，宗门长老",
                    "events": "穿越事件，发现修仙可以编程化",
                    "conflicts": "适应新世界，理解修仙体系",
                    "turning_points": "第一次成功用代码思维修炼",
                    "emotional_tone": "困惑中带着兴奋",
                    "foreshadowing": "暗示修仙世界的系统性质"
                },
                {
                    "number": 2,
                    "title": "功法重构",
                    "scenes": "宗门练功房，藏经阁",
                    "characters": "主角，师兄师姐，神秘长老",
                    "events": "重构传统功法，引发宗门关注",
                    "conflicts": "传统派与革新派的对立",
                    "turning_points": "功法重构成功，实力大增",
                    "emotional_tone": "紧张刺激",
                    "foreshadowing": "更深层的世界秘密"
                },
                {
                    "number": 3,
                    "title": "系统升级",
                    "scenes": "宗门大殿，神秘空间",
                    "characters": "主角，宗主，系统意识",
                    "events": "发现世界真相，与系统对话",
                    "conflicts": "选择改变世界还是维持现状",
                    "turning_points": "决定升级整个修仙世界的系统",
                    "emotional_tone": "震撼与决心",
                    "foreshadowing": "更大的冒险即将开始"
                }
            ]
        }
    }
    
    response = requests.post(f"{base_url}/projects/{project_id}/plot-outlines", json=plot_data)
    if response.status_code != 200:
        print(f"❌ 大纲创建失败: {response.status_code}")
        return False
    
    plot_outline = response.json()
    plot_id = plot_outline["id"]
    print(f"✅ 大纲创建成功: {plot_outline['title']}")
    
    # 选中大纲
    response = requests.patch(f"{base_url}/projects/{project_id}/plot-outlines/{plot_id}", 
                             json={"is_selected": True})
    if response.status_code == 200:
        print("✅ 大纲已选中")
    
    # 5. 创建人物设定
    print("\n5. 创建人物设定")
    character_data = {
        "name": "主角人物设定",
        "content": {
            "set_number": 1,
            "characters": [
                {
                    "基本信息": {
                        "姓名": "李程",
                        "性别": "男",
                        "年龄": "25岁",
                        "种族": "人类",
                        "外貌特征": ["中等身材", "戴眼镜", "程序员气质"],
                        "衣着风格": "简约休闲，后期修仙道袍"
                    },
                    "背景故事": "原本是一名资深程序员，因为一次意外穿越到修仙世界。发现修仙体系与编程有惊人的相似性。",
                    "性格特质": {
                        "核心性格": "理性分析型",
                        "价值观": "用科学方法理解一切",
                        "优点": ["逻辑思维强", "学习能力强", "创新思维"],
                        "缺点": ["过度理性", "缺乏直觉", "社交能力一般"],
                        "癖好": "喜欢把一切都用代码逻辑来解释",
                        "口头禅": "这个可以优化"
                    },
                    "能力技能": {
                        "技能": ["编程", "系统分析", "算法优化"],
                        "知识": ["计算机科学", "软件工程", "逐渐学习修仙知识"],
                        "特殊能力": "能够将修仙功法转化为代码逻辑",
                        "力量等级": "初期练气，快速提升"
                    },
                    "动机与目标": {
                        "内心驱动力": "用现代思维改造修仙世界",
                        "短期目标": "掌握基础修仙技能，在宗门立足",
                        "长期目标": "发现修仙世界的系统本质，实现世界升级"
                    },
                    "角色弧光": "从困惑的穿越者成长为改变世界的革新者",
                    "人际关系": [
                        {
                            "关系对象": "师父",
                            "关系类型": "师徒",
                            "关系描述": "开明的长老，支持主角的创新思维"
                        }
                    ]
                }
            ],
            "description": "以程序员思维重新定义修仙的主角设定"
        }
    }
    
    response = requests.post(f"{base_url}/projects/{project_id}/characters", json=character_data)
    if response.status_code != 200:
        print(f"❌ 人物设定创建失败: {response.status_code}")
        return False
    
    character = response.json()
    char_id = character["id"]
    print(f"✅ 人物设定创建成功: {character['name']}")
    
    # 选中人物设定
    response = requests.patch(f"{base_url}/projects/{project_id}/characters/{char_id}", 
                             json={"is_selected": True})
    if response.status_code == 200:
        print("✅ 人物设定已选中")
    
    # 6. 生成第一章
    print("\n6. 生成第一章")
    chapter_data = {
        "chapter_outline": {
            "number": 1,
            "title": "代码觉醒",
            "scenes": "现代办公室，修仙世界入门宗门",
            "characters": "主角李程，宗门长老",
            "events": "穿越事件，发现修仙可以编程化",
            "conflicts": "适应新世界，理解修仙体系",
            "turning_points": "第一次成功用代码思维修炼",
            "emotional_tone": "困惑中带着兴奋",
            "foreshadowing": "暗示修仙世界的系统性质"
        },
        "world_setting": world_data["content"],
        "character_profiles": [character_data["content"]],
        "previous_summary": "",
        "kb_context": [],
        "writing_style": "详细生动"
    }
    
    print("正在生成章节，请稍候...")
    response = requests.post(f"{base_url}/projects/{project_id}/chapters", 
                           json=chapter_data, timeout=120)
    
    if response.status_code != 200:
        print(f"❌ 章节生成失败: {response.status_code}")
        print(f"错误信息: {response.text}")
        return False
    
    chapter = response.json()
    print(f"✅ 第一章生成成功!")
    print(f"章节ID: {chapter['id'][:8]}...")
    print(f"章节标题: {chapter['title']}")
    print(f"内容长度: {chapter['word_count']} 字")
    print(f"内容预览: {chapter['content'][:100]}...")
    
    # 7. 验证章节列表
    print("\n7. 验证章节列表")
    response = requests.get(f"{base_url}/projects/{project_id}/chapters")
    if response.status_code == 200:
        chapters = response.json()
        print(f"✅ 项目当前有 {len(chapters)} 个章节")
        for ch in chapters:
            print(f"  第{ch['chapter_number']}章: {ch['title']}")
    else:
        print(f"❌ 获取章节列表失败: {response.status_code}")
    
    print("\n=== 测试完成 ===")
    print("🎉 统一数据库系统测试成功！")
    print(f"测试项目ID: {project_id}")
    print("现在您可以在前端看到这个项目和生成的章节了！")
    
    return True

if __name__ == "__main__":
    success = test_unified_system()
    if not success:
        print("❌ 测试失败")
        exit(1)
