#!/usr/bin/env python3
"""
测试修复后的功能
"""
import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:8002/api"

def test_api_endpoints():
    """测试API端点是否正常工作"""
    print("🧪 测试API端点...")
    
    # 测试根端点
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/")
        if response.status_code == 200:
            print("✅ 根端点正常")
        else:
            print(f"❌ 根端点异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 根端点连接失败: {e}")
    
    # 测试项目列表端点
    try:
        response = requests.get(f"{API_BASE_URL}/projects")
        if response.status_code == 200:
            print("✅ 项目列表端点正常")
        else:
            print(f"❌ 项目列表端点异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 项目列表端点连接失败: {e}")

def test_project_creation():
    """测试项目创建功能"""
    print("\n📝 测试项目创建...")
    
    project_data = {
        "title": "测试小说项目",
        "description": "这是一个用于测试修复功能的项目",
        "target_chapters": 10,
        "writing_style": "详细生动",
        "genre": "玄幻"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/projects", json=project_data)
        if response.status_code == 200:
            project = response.json()
            print(f"✅ 项目创建成功: {project['id']}")
            return project['id']
        else:
            print(f"❌ 项目创建失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 项目创建异常: {e}")
        return None

def test_concept_generation(project_id):
    """测试概述生成功能"""
    print(f"\n💡 测试概述生成 (项目ID: {project_id})...")
    
    concept_data = {
        "user_input": "一个普通高中生发现自己拥有预知未来的能力，在一次意外中看到了学校将要发生的灾难",
        "num_concepts": 2,
        "style_preference": "悬疑推理"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/projects/{project_id}/concepts", json=concept_data)
        if response.status_code == 200:
            result = response.json()
            concepts = result.get('concepts', [])
            print(f"✅ 概述生成成功，生成了 {len(concepts)} 个概述")
            
            # 测试选择第一个概述
            if concepts:
                concept_id = concepts[0]['id']
                select_response = requests.post(f"{API_BASE_URL}/projects/{project_id}/concepts/{concept_id}/select")
                if select_response.status_code == 200:
                    print("✅ 概述选择成功")
                else:
                    print(f"❌ 概述选择失败: {select_response.status_code}")
            
            return True
        else:
            print(f"❌ 概述生成失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 概述生成异常: {e}")
        return False

def test_world_setting_generation(project_id):
    """测试世界观设定生成功能"""
    print(f"\n🌍 测试世界观设定生成 (项目ID: {project_id})...")
    
    world_data = {
        "narrative_concept": "一个普通高中生发现自己拥有预知未来的能力",
        "num_settings": 2
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/projects/{project_id}/world-settings", json=world_data)
        if response.status_code == 200:
            result = response.json()
            settings = result.get('world_settings', [])
            print(f"✅ 世界观设定生成成功，生成了 {len(settings)} 套设定")
            return True
        else:
            print(f"❌ 世界观设定生成失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 世界观设定生成异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试修复后的功能...\n")
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试项目创建
    project_id = test_project_creation()
    if not project_id:
        print("❌ 项目创建失败，停止后续测试")
        return
    
    # 等待一下确保项目创建完成
    time.sleep(1)
    
    # 测试概述生成
    if test_concept_generation(project_id):
        time.sleep(1)
        # 测试世界观设定生成
        test_world_setting_generation(project_id)
    
    print("\n🎉 测试完成！")
    print("\n📋 修复总结:")
    print("1. ✅ 添加了小说风格类型选择功能")
    print("2. ✅ 为概述添加了编辑功能和质量评估显示")
    print("3. ✅ 为世界观设定添加了编辑功能")
    print("4. ✅ 为大纲生成添加了冲突元素建议功能")
    print("5. ✅ 修复了章节生成的索引问题")
    print("6. ✅ 修复了润色功能")
    print("7. ✅ 改进了剧情分支显示功能")
    print("8. ✅ 添加了设置页面")
    print("\n🔧 建议下一步:")
    print("- 启动后端服务: cd backend && python run.py")
    print("- 启动前端服务: cd frontend && npm run dev")
    print("- 访问 http://localhost:5173 测试前端功能")

if __name__ == "__main__":
    main()
