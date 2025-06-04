#!/usr/bin/env python3
"""
测试当前修复效果的综合测试脚本
"""
import requests
import json
import time
import sys

API_BASE_URL = "http://localhost:8002/api"

def test_api_health():
    """测试API健康状态"""
    print("🔍 测试API健康状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API服务正常运行")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_project_creation():
    """测试项目创建"""
    print("\n📝 测试项目创建...")
    try:
        payload = {
            "title": "修复效果测试项目",
            "description": "用于测试各项修复功能的项目",
            "target_chapters": 10,
            "writing_style": "详细生动",
            "genre": "科幻"
        }
        
        response = requests.post(f"{API_BASE_URL}/projects", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            project_id = data["id"]
            print(f"✅ 项目创建成功: {project_id}")
            return project_id
        else:
            print(f"❌ 项目创建失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 项目创建异常: {e}")
        return None

def test_concept_generation_count(project_id):
    """测试概述生成数量功能"""
    print(f"\n💡 测试概述生成数量功能 (项目ID: {project_id})...")
    
    # 测试生成1个概述
    print("🧪 测试生成1个概述...")
    try:
        payload = {
            "user_input": "一个关于时间旅行的科幻故事，主角发现了改变过去的能力",
            "num_concepts": 1
        }
        
        response = requests.post(f"{API_BASE_URL}/projects/{project_id}/concepts", 
                               json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            concepts_count = len(data.get("concepts", []))
            print(f"✅ 请求生成1个概述，实际生成了 {concepts_count} 个概述")
            if concepts_count == 1:
                print("✅ 概述数量控制功能正常")
                return True
            else:
                print("⚠️ 概述数量与请求不符")
                return False
        else:
            print(f"❌ 概述生成失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 概述生成异常: {e}")
        return False

def test_concept_editing(project_id):
    """测试概述编辑功能"""
    print(f"\n✏️ 测试概述编辑功能...")
    try:
        # 获取概述列表
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}/concepts", timeout=15)
        if response.status_code == 200:
            data = response.json()
            concepts = data.get("concepts", [])
            if concepts:
                concept_id = concepts[0]["id"]
                
                # 测试编辑概述
                edit_payload = {
                    "content": "这是一个编辑后的概述内容，用于测试编辑功能。"
                }
                
                response = requests.put(f"{API_BASE_URL}/projects/{project_id}/concepts/{concept_id}", 
                                      json=edit_payload, timeout=15)
                if response.status_code == 200:
                    print("✅ 概述编辑功能正常")
                    return True
                else:
                    print(f"❌ 概述编辑失败: {response.status_code}")
                    return False
            else:
                print("❌ 没有找到可编辑的概述")
                return False
        else:
            print(f"❌ 获取概述列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 概述编辑测试异常: {e}")
        return False

def test_world_setting_generation(project_id):
    """测试世界观设定生成"""
    print(f"\n🌍 测试世界观设定生成...")
    try:
        # 先选择一个概述
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}/concepts", timeout=15)
        if response.status_code == 200:
            data = response.json()
            concepts = data.get("concepts", [])
            if concepts:
                concept_id = concepts[0]["id"]
                # 选择概述
                requests.post(f"{API_BASE_URL}/projects/{project_id}/concepts/{concept_id}/select", timeout=15)
                
                # 生成世界观设定
                payload = {"num_settings": 2}
                response = requests.post(f"{API_BASE_URL}/projects/{project_id}/world-settings", 
                                       json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    settings_count = len(data.get("world_settings", []))
                    print(f"✅ 世界观设定生成成功，生成了 {settings_count} 个设定")
                    return True
                else:
                    print(f"❌ 世界观设定生成失败: {response.status_code}")
                    print(response.text)
                    return False
            else:
                print("❌ 没有找到概述")
                return False
        else:
            print(f"❌ 获取概述失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 世界观设定生成异常: {e}")
        return False

def test_plot_outline_generation(project_id):
    """测试大纲生成和编辑功能"""
    print(f"\n📋 测试大纲生成功能...")
    try:
        # 先选择世界观设定
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}/world-settings", timeout=15)
        if response.status_code == 200:
            data = response.json()
            settings = data.get("world_settings", [])
            if settings:
                setting_id = settings[0]["id"]
                # 选择世界观设定
                requests.post(f"{API_BASE_URL}/projects/{project_id}/world-settings/{setting_id}/select", timeout=15)
                
                # 生成大纲
                payload = {
                    "chapter_count": 15,  # 测试自定义章节数量
                    "conflict_elements": "主角与反派的对抗\n时间悖论的挑战"
                }
                response = requests.post(f"{API_BASE_URL}/projects/{project_id}/plot-outlines", 
                                       json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    outlines_count = len(data.get("plot_outlines", []))
                    print(f"✅ 大纲生成成功，生成了 {outlines_count} 个大纲")
                    return True
                else:
                    print(f"❌ 大纲生成失败: {response.status_code}")
                    print(response.text)
                    return False
            else:
                print("❌ 没有找到世界观设定")
                return False
        else:
            print(f"❌ 获取世界观设定失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 大纲生成异常: {e}")
        return False

def test_character_generation(project_id):
    """测试人物设定生成"""
    print(f"\n👥 测试人物设定生成...")
    try:
        # 先选择大纲
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}/plot-outlines", timeout=15)
        if response.status_code == 200:
            data = response.json()
            outlines = data.get("plot_outlines", [])
            if outlines:
                outline_id = outlines[0]["id"]
                # 选择大纲
                requests.post(f"{API_BASE_URL}/projects/{project_id}/plot-outlines/{outline_id}/select", timeout=15)
                
                # 生成人物设定
                payload = {"num_character_sets": 3}  # 测试增加的数量选项
                response = requests.post(f"{API_BASE_URL}/projects/{project_id}/characters", 
                                       json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    characters_count = len(data.get("characters", []))
                    print(f"✅ 人物设定生成成功，生成了 {characters_count} 个人物设定")
                    return True
                else:
                    print(f"❌ 人物设定生成失败: {response.status_code}")
                    print(response.text)
                    return False
            else:
                print("❌ 没有找到大纲")
                return False
        else:
            print(f"❌ 获取大纲失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 人物设定生成异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试当前修复效果...\n")
    
    # 测试API健康状态
    if not test_api_health():
        print("❌ API服务不可用，停止测试")
        return
    
    # 测试项目创建
    project_id = test_project_creation()
    if not project_id:
        print("❌ 项目创建失败，停止后续测试")
        return
    
    # 等待一下确保项目创建完成
    time.sleep(1)
    
    # 测试各项功能
    results = []
    
    # 测试概述生成数量
    results.append(("概述生成数量控制", test_concept_generation_count(project_id)))
    time.sleep(1)
    
    # 测试概述编辑
    results.append(("概述编辑功能", test_concept_editing(project_id)))
    time.sleep(1)
    
    # 测试世界观设定生成
    results.append(("世界观设定生成", test_world_setting_generation(project_id)))
    time.sleep(1)
    
    # 测试大纲生成
    results.append(("大纲生成功能", test_plot_outline_generation(project_id)))
    time.sleep(1)
    
    # 测试人物设定生成
    results.append(("人物设定生成", test_character_generation(project_id)))
    
    # 输出测试结果总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！修复效果良好。")
    elif passed > total // 2:
        print("⚠️ 大部分功能正常，但仍有一些问题需要解决。")
    else:
        print("❌ 多项功能存在问题，需要进一步修复。")
    
    print(f"\n🔧 测试项目ID: {project_id}")
    print("您可以在前端界面中进一步测试编辑功能和UI改进。")

if __name__ == "__main__":
    main()
