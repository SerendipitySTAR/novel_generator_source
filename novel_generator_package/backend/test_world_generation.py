#!/usr/bin/env python3
"""
测试世界观生成功能
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import init_db
from app.db.database import get_db
from app.db.repositories import ConceptRepository, WorldSettingRepository
from app.models import Project, Concept
from app.services.novel_generation_service import NovelGenerationService
from app.core.llm import OpenAILLM
import uuid

async def test_world_generation():
    """测试世界观生成功能"""
    print("开始测试世界观生成功能...")
    
    # 初始化数据库
    print("1. 初始化数据库...")
    init_db()
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 创建测试项目
        print("2. 创建测试项目...")
        project = Project(
            id=str(uuid.uuid4()),
            title='测试项目',
            description='用于测试世界观生成',
            status='active'
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"   项目ID: {project.id}")
        
        # 创建测试概述
        print("3. 创建测试概述...")
        concept = Concept(
            id=str(uuid.uuid4()),
            project_id=project.id,
            title='测试概述',
            content='这是一个关于魔法世界的小说，主角是一个年轻的法师，他要拯救世界免受黑暗势力的侵害。',
            is_selected=True,
            order_index=0
        )
        db.add(concept)
        db.commit()
        db.refresh(concept)
        print(f"   概述ID: {concept.id}")
        
        # 验证概述是否正确保存
        print("4. 验证概述数据...")
        concept_repo = ConceptRepository(db)
        selected = concept_repo.get_selected_by_project_id(project.id)
        if selected:
            print(f"   找到选中的概述: {selected.id}")
            print(f"   概述内容: {selected.content[:50]}...")
        else:
            print("   错误：未找到选中的概述")
            return
        
        # 创建服务实例
        print("5. 创建服务实例...")
        llm = OpenAILLM()
        service = NovelGenerationService(db)
        
        # 测试世界观生成
        print("6. 开始生成世界观设定...")
        try:
            world_settings = await service.generate_world_settings(
                project_id=project.id,
                num_settings=2
            )
            
            print(f"   成功生成 {len(world_settings)} 个世界观设定")
            for i, ws in enumerate(world_settings):
                print(f"   世界观 {i+1}: {ws.title}")
                print(f"   内容类型: {type(ws.content)}")
                if isinstance(ws.content, dict):
                    print(f"   包含部分: {list(ws.content.keys())}")
                
        except Exception as e:
            print(f"   世界观生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()
        print("测试完成")

if __name__ == "__main__":
    asyncio.run(test_world_generation())
