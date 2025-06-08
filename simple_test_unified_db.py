#!/usr/bin/env python3
"""
简单测试统一数据库 - 直接在数据库中创建测试数据
"""
import sqlite3
import json
import uuid
from datetime import datetime

def create_test_data():
    """创建测试数据"""
    print("=== 创建测试数据验证数据库统一 ===")
    
    db_path = "./novel_generator.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 创建测试项目
        project_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO projects (id, title, description, status, target_chapters, writing_style, genre, project_metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, "数据库统一测试项目", "验证前后端使用同一数据库", "created", 
            3, "详细生动", "修仙", "{}", now, now
        ))
        
        print(f"✅ 项目创建成功: {project_id}")
        
        # 2. 创建概述
        concept_id = str(uuid.uuid4())
        concept_content = """**核心概念**：
一个现代程序员意外穿越到修仙世界，发现修仙体系可以用编程思维优化。

**主要冲突**：
1. 现代科学思维与传统修仙理念的碰撞
2. 用代码逻辑优化修炼功法引发的宗门争议  
3. 发现修仙世界背后隐藏的"系统"真相

**故事亮点**：
- 用编程思维重新解构修仙体系
- 将修炼功法转化为可执行的"代码"
- 探索修仙世界的底层"操作系统" """
        
        cursor.execute("""
            INSERT INTO concepts (id, project_id, title, content, expanded_content, is_selected, order_index, quality_score, evaluation_result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            concept_id, project_id, "编程修仙概述", concept_content, "", True, 1, 85, json.dumps({"score": 85, "comment": "优秀"}), now, now
        ))
        
        print(f"✅ 概述创建成功: {concept_id}")
        
        # 3. 创建世界观
        world_id = str(uuid.uuid4())
        world_content = {
            "description": "一个修仙与编程融合的奇幻世界",
            "sections": {
                "基础设定": "修仙者通过'灵力编程'来施展法术，每个功法都是一段可执行的代码",
                "地理环境": "各大宗门如同不同的开发团队，拥有各自的编程语言和框架",
                "修炼体系": "从初级程序员（练气期）到架构师（元婴期）的完整修炼路径",
                "特殊规则": "修仙世界存在'天道编译器'，会检查和优化所有修炼者的'代码'"
            }
        }
        
        cursor.execute("""
            INSERT INTO world_settings (id, project_id, title, content, is_selected, order_index, quality_score, evaluation_result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            world_id, project_id, "修仙编程世界", json.dumps(world_content), True, 1, 90, json.dumps({"score": 90, "comment": "优秀"}), now, now
        ))
        
        print(f"✅ 世界观创建成功: {world_id}")
        
        # 4. 创建大纲
        plot_id = str(uuid.uuid4())
        plot_content = {
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
        
        cursor.execute("""
            INSERT INTO plot_outlines (id, project_id, title, content, is_selected, order_index, quality_score, evaluation_result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            plot_id, project_id, "编程修仙大纲", json.dumps(plot_content), True, 1, 88, json.dumps({"score": 88, "comment": "优秀"}), now, now
        ))
        
        print(f"✅ 大纲创建成功: {plot_id}")
        
        # 5. 创建人物设定
        char_id = str(uuid.uuid4())
        char_content = {
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
        
        cursor.execute("""
            INSERT INTO characters (id, project_id, name, content, is_selected, order_index, character_type, quality_score, evaluation_result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            char_id, project_id, "主角人物设定", json.dumps(char_content), True, 1, "main", 87, json.dumps({"score": 87, "comment": "优秀"}), now, now
        ))
        
        print(f"✅ 人物设定创建成功: {char_id}")
        
        # 6. 创建第一章
        chapter_id = str(uuid.uuid4())
        chapter_content = """第一章 代码觉醒

李程盯着屏幕上密密麻麻的代码，眼皮越来越重。作为一名资深的全栈开发工程师，他已经连续工作了十八个小时，只为了修复一个诡异的并发bug。

"又是一个死锁问题..."他揉了揉太阳穴，正准备再次调试时，屏幕突然闪烁起来。

代码行开始自动滚动，仿佛有了生命一般。李程惊讶地发现，这些代码竟然在重新组合，形成了一种他从未见过的编程语言。

"这是什么鬼..."

话音未落，一道刺眼的白光从屏幕中射出，瞬间将他吞没。

当李程再次睁开眼睛时，发现自己躺在一个古色古香的房间里。木质的床榻，青石的地面，还有空气中淡淡的檀香味，一切都显得那么陌生。

"这位师弟，你终于醒了。"

一个穿着道袍的中年男子走了进来，脸上带着温和的笑容。

"师弟？道袍？"李程坐起身来，脑海中一片混乱，"这是在拍戏吗？"

"师弟莫要惊慌，你是在渡劫时被雷劫震伤，昏迷了三天。我是你的师兄王明轩。"

渡劫？雷劫？李程感觉自己的世界观正在崩塌。他低头看了看自己，发现身上穿的也是一身青色道袍。

"等等，你说渡劫？"李程试图理解这个情况，"你的意思是...修仙？"

王明轩点了点头："正是。师弟你失忆了吗？我们都是浮云宗的弟子，你正在练气期巅峰，准备突破筑基。"

李程的程序员大脑开始快速运转。如果这不是梦，那么只有一种可能——他穿越了。

"能告诉我，修仙是怎么回事吗？"李程决定先收集信息。

王明轩详细地为他解释了修仙的基本概念：通过修炼功法，吸收天地灵气，强化身体和神魂，最终达到长生不老的境界。

听着这些解释，李程的眼睛越来越亮。作为一个程序员，他敏锐地察觉到了其中的规律性。

"所以说，功法就像是一套算法，灵气是数据输入，身体是硬件，神魂是操作系统？"

王明轩愣了一下："师弟，你说的这些词汇很奇怪，但...似乎有些道理。"

李程兴奋起来。如果修仙真的可以用编程思维来理解，那他这个程序员岂不是有天然的优势？

"师兄，能教我一些基础的功法吗？"

王明轩取出一本《基础吐纳术》："这是最简单的功法，用于感知和吸收灵气。"

李程接过功法秘籍，仔细阅读起来。在他的理解中，这套功法就像是一个循环算法：

```
while (修炼中) {
    感知灵气();
    吸收灵气();
    炼化灵气();
    存储到丹田();
}
```

"有趣..."李程按照功法描述开始修炼。

令人惊讶的是，当他用编程思维去理解功法时，修炼效果竟然出奇的好。原本需要数月才能掌握的基础吐纳术，他在短短一个时辰内就入门了。

王明轩在一旁看得目瞪口呆："师弟，你的天赋...简直闻所未闻！"

李程心中暗喜。看来他的猜测是对的——这个修仙世界的底层逻辑，确实可以用编程思维来理解和优化。

"师兄，还有更高级的功法吗？"

"有是有，但那些都是宗门核心功法，需要达到筑基期才能修炼。"王明轩犹豫了一下，"不过...师弟既然天赋如此出众，我可以带你去见见长老。"

李程点头同意。他迫不及待地想要了解这个世界更深层的"系统架构"。

当晚，在王明轩的引荐下，李程见到了负责外门弟子的张长老。这位白发苍苍的老者听说了李程的情况后，决定亲自测试他的修炼天赋。

"小友，请运转你刚学会的吐纳术。"

李程盘腿而坐，开始运转功法。在他的意识中，这不再是什么玄妙的修仙术法，而是一段优雅的代码在执行。

张长老的眼中闪过一丝惊讶。他能感受到，这个年轻弟子体内的灵气运转轨迹异常规整，效率也远超常人。

"奇哉怪哉..."张长老抚须沉思，"小友，你可愿意成为老夫的亲传弟子？"

李程心中一喜，这意味着他将有机会接触到更高级的"系统权限"。

"弟子愿意！"

就这样，李程正式踏上了用编程思维重新定义修仙的道路。他不知道的是，这个看似古老的修仙世界，背后隐藏着一个更加庞大的"系统"秘密..."""
        
        cursor.execute("""
            INSERT INTO chapters (id, project_id, chapter_number, title, content, outline, status, word_count, quality_score, evaluation_result, writing_style, generation_metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chapter_id, project_id, 1, "代码觉醒", chapter_content,
            json.dumps(plot_content["chapter_details"][0]), "draft", len(chapter_content),
            85, json.dumps({"score": 85, "comment": "优秀"}), "详细生动", "{}", now, now
        ))
        
        print(f"✅ 第一章创建成功: {chapter_id}")
        print(f"章节内容长度: {len(chapter_content)} 字")
        
        # 提交所有更改
        conn.commit()
        
        print(f"\n=== 测试数据创建完成 ===")
        print(f"项目ID: {project_id}")
        print("现在您可以在前端看到这个完整的测试项目了！")
        
        return project_id
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    project_id = create_test_data()
    if project_id:
        print(f"\n🎉 数据库统一测试成功！")
        print(f"测试项目ID: {project_id}")
        print("请刷新前端页面查看测试项目和章节")
    else:
        print("\n❌ 测试失败")
