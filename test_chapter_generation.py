import requests
import json

# 测试章节生成API
def test_chapter_generation():
    project_id = "2a230931-17cd-4584-8d79-cfa14811be78"
    api_url = f"http://localhost:8002/api/projects/{project_id}/chapters"
    
    # 构造请求数据 - 测试第二章
    chapter_outline = {
        "number": 2,
        "title": "《浮云宗的真相》",
        "scenes": "浮云宗内院，长老议事厅，禁地入口",
        "characters": "苏晚，周昊长老，神秘黑衣人",
        "events": "苏晚被逐出宗门，发现宗门隐藏的秘密",
        "conflicts": "身份暴露，追杀开始，信任危机",
        "turning_points": "发现仙陨石碎片的真正来源",
        "emotional_tone": "紧张悬疑",
        "foreshadowing": "三万年前仙魔大战的线索",
        "word_count": "4000"
    }
    
    world_setting = {
        "description": "逆天道的混沌螺旋",
        "sections": {
            "基础设定": "宇宙结构：真仙界-凡俗界-混沌海三层结构",
            "地理环境": "天墟城、浮云山脉、仙陨禁地",
            "历史背景": "三万年前仙魔大战，仙陨石碎片散落",
            "主要势力": "天一门、天机阁、混沌守卫团",
            "能量体系": "传统仙道与混沌之力双轨制",
            "文化与社会": "渡劫成功者为天命之子的等级制度",
            "特殊生物": "混沌兽、仙陨石、天墟兽"
        }
    }
    
    character_profiles = [
        {
            "姓名": "苏晚",
            "性别": "女",
            "年龄": "18",
            "背景": "出身青石镇苏氏家族，资质平庸的修仙者",
            "性格": "隐忍而坚韧，善解人意但过度自我否定",
            "能力": "劫云吞噬，基础阵法布置",
            "目标": "证明自己不是累赘，解开仙陨石碎片之谜"
        }
    ]
    
    request_data = {
        "chapter_outline": chapter_outline,
        "world_setting": world_setting,
        "character_profiles": character_profiles,
        "previous_summary": "苏晚在渡劫失败后，体内的仙陨石碎片觉醒，获得了劫云吞噬的能力。混沌兽从劫云中诞生，与她形成共生关系。浮云宗的弟子们目睹了这一切，周昊长老认出了逆天道的混沌螺旋，建议她前往仙陨禁地。",
        "kb_context": [],
        "writing_style": "详细生动"
    }
    
    print("=== 测试章节生成API ===")
    print(f"项目ID: {project_id}")
    print(f"API URL: {api_url}")
    print(f"请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=300  # 5分钟超时
        )
        
        print(f"\n=== 响应信息 ===")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"成功！章节生成结果:")
            print(f"章节ID: {result.get('id')}")
            print(f"章节号: {result.get('chapter_number')}")
            print(f"标题: {result.get('title')}")
            print(f"内容长度: {len(result.get('content', ''))}")
            print(f"内容预览: {result.get('content', '')[:200]}...")
        else:
            print(f"失败！错误信息:")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"响应文本: {response.text}")
                
    except requests.exceptions.Timeout:
        print("请求超时！可能是AI服务响应慢或者生成过程耗时较长")
    except requests.exceptions.ConnectionError:
        print("连接错误！请检查后端服务是否正常运行")
    except Exception as e:
        print(f"其他错误: {str(e)}")

if __name__ == "__main__":
    test_chapter_generation()
