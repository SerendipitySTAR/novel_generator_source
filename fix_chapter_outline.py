import requests
import json

def fix_chapter_outline():
    """修复章节大纲的详细信息"""
    project_id = "2a230931-17cd-4584-8d79-cfa14811be78"
    
    # 获取当前项目信息
    response = requests.get(f"http://localhost:8002/api/projects/{project_id}")
    if response.status_code != 200:
        print(f"获取项目失败: {response.status_code}")
        return
    
    project_data = response.json()
    plot_outline = project_data["selected_items"]["plot_outline"]
    
    print("当前大纲信息:")
    print(f"大纲ID: {plot_outline['id']}")
    print(f"大纲标题: {plot_outline['title']}")
    
    # 修复章节详情
    updated_chapter_details = [
        {
            "number": 1,
            "title": "《坠落的劫云》",
            "scenes": "渡劫失败现场，浮云宗山门，混沌裂缝边缘",
            "characters": "苏晚，混沌兽，天元宗长老",
            "events": "苏晚渡劫失败，仙陨石碎片觉醒，混沌兽诞生",
            "conflicts": "生存危机，力量失控，身份暴露",
            "turning_points": "劫云吞噬能力觉醒",
            "emotional_tone": "绝望中的希望",
            "foreshadowing": "仙陨石碎片的神秘力量"
        },
        {
            "number": 2,
            "title": "《浮云宗的真相》",
            "scenes": "浮云宗内院，长老议事厅，禁地入口",
            "characters": "苏晚，周昊长老，神秘黑衣人",
            "events": "苏晚被逐出宗门，发现宗门隐藏的秘密",
            "conflicts": "身份暴露，追杀开始，信任危机",
            "turning_points": "发现仙陨石碎片的真正来源",
            "emotional_tone": "紧张悬疑",
            "foreshadowing": "三万年前仙魔大战的线索"
        },
        {
            "number": 3,
            "title": "《混沌潮汐之夜》",
            "scenes": "仙陨禁地，混沌裂缝深处，天墟城边缘",
            "characters": "苏晚，混沌兽，齐静真仙",
            "events": "混沌潮汐爆发，苏晚与混沌兽深度融合",
            "conflicts": "力量失控，人性异化，追兵逼近",
            "turning_points": "遇到隐世真仙齐静",
            "emotional_tone": "震撼壮观",
            "foreshadowing": "真仙界崩塌的历史真相"
        },
        {
            "number": 4,
            "title": "《青铜古镜的低语》",
            "scenes": "天机阁密室，青铜古镜前，记忆幻境",
            "characters": "苏晚，齐静，沈明远，历史幻影",
            "events": "通过青铜古镜回溯历史，揭开仙魔大战真相",
            "conflicts": "历史真相的冲击，道德选择的困境",
            "turning_points": "发现自己与三万年前事件的关联",
            "emotional_tone": "沉重震撼",
            "foreshadowing": "最终决战的预兆"
        },
        {
            "number": 5,
            "title": "《天墟城的裂痕》",
            "scenes": "天墟城，天罚阁总部，混沌螺旋核心",
            "characters": "苏晚，沈明远，混沌兽，所有势力",
            "events": "最终决战，混沌螺旋的终极秘密揭晓",
            "conflicts": "正邪对决，宿命抗争，自我救赎",
            "turning_points": "选择拯救还是毁灭",
            "emotional_tone": "史诗悲壮",
            "foreshadowing": "新纪元的开始"
        }
    ]
    
    # 更新大纲内容
    updated_content = plot_outline["content"].copy()
    updated_content["chapter_details"] = updated_chapter_details
    
    # 发送更新请求
    update_data = {
        "content": updated_content
    }
    
    update_url = f"http://localhost:8002/api/projects/{project_id}/plot-outlines/{plot_outline['id']}"
    
    print(f"\n正在更新大纲...")
    print(f"更新URL: {update_url}")
    
    response = requests.put(
        update_url,
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✅ 大纲更新成功！")
        result = response.json()
        print(f"更新后的章节数量: {len(result.get('content', {}).get('chapter_details', []))}")
        
        # 验证更新结果
        print("\n验证更新结果:")
        for i, chapter in enumerate(updated_chapter_details):
            print(f"第{chapter['number']}章: {chapter['title']}")
            print(f"  场景: {chapter['scenes']}")
            print(f"  人物: {chapter['characters']}")
            print(f"  事件: {chapter['events']}")
            print()
            
    else:
        print(f"❌ 大纲更新失败: {response.status_code}")
        try:
            error_data = response.json()
            print(f"错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
        except:
            print(f"响应文本: {response.text}")

if __name__ == "__main__":
    fix_chapter_outline()
