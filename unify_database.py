#!/usr/bin/env python3
"""
统一数据库脚本：删除所有现有数据库，创建统一的数据库配置
"""
import os
import shutil
import sqlite3

def unify_database():
    """统一数据库配置"""
    print("开始统一数据库配置...")
    
    # 定义所有可能的数据库文件路径
    db_files = [
        "./novel_generator.db",
        "./novel_generator_package/backend/novel_generator.db", 
        "./novel_generator_package/frontend/novel_generator.db"
    ]
    
    # 1. 删除所有现有数据库文件
    print("\n=== 清理现有数据库文件 ===")
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"删除: {db_file}")
            os.remove(db_file)
        else:
            print(f"不存在: {db_file}")
    
    # 2. 统一使用根目录的数据库
    unified_db_path = "./novel_generator.db"
    print(f"\n=== 创建统一数据库: {unified_db_path} ===")
    
    # 3. 创建数据库表结构
    conn = sqlite3.connect(unified_db_path)
    cursor = conn.cursor()
    
    # 创建项目表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'created',
            target_chapters INTEGER DEFAULT 10,
            writing_style TEXT DEFAULT '详细生动',
            genre TEXT,
            project_metadata TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    
    # 创建概述表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concepts (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            expanded_content TEXT,
            is_selected BOOLEAN DEFAULT FALSE,
            order_index INTEGER,
            quality_score INTEGER,
            evaluation_result TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    # 创建世界观表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS world_settings (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            is_selected BOOLEAN DEFAULT FALSE,
            order_index INTEGER,
            quality_score INTEGER,
            evaluation_result TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    # 创建大纲表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plot_outlines (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            is_selected BOOLEAN DEFAULT FALSE,
            order_index INTEGER,
            quality_score INTEGER,
            evaluation_result TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    # 创建人物表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            is_selected BOOLEAN DEFAULT FALSE,
            order_index INTEGER,
            character_type TEXT DEFAULT 'main',
            quality_score INTEGER,
            evaluation_result TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    # 创建章节表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chapters (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            chapter_number INTEGER NOT NULL,
            title TEXT,
            content TEXT,
            outline TEXT,
            status TEXT DEFAULT 'draft',
            word_count INTEGER DEFAULT 0,
            quality_score INTEGER,
            evaluation_result TEXT,
            writing_style TEXT,
            generation_metadata TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ 统一数据库创建完成")
    
    # 4. 更新后端数据库配置
    print("\n=== 更新后端数据库配置 ===")
    backend_db_config = "./novel_generator_package/backend/app/db/database.py"
    
    if os.path.exists(backend_db_config):
        with open(backend_db_config, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新数据库路径为根目录
        new_content = content.replace(
            'DATABASE_URL = "sqlite:///./novel_generator.db"',
            'DATABASE_URL = "sqlite:///../../novel_generator.db"'
        )
        
        with open(backend_db_config, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 后端数据库配置已更新")
    else:
        print("❌ 后端数据库配置文件不存在")
    
    # 5. 创建符号链接（可选）
    print("\n=== 创建符号链接 ===")
    backend_link = "./novel_generator_package/backend/novel_generator.db"
    if not os.path.exists(backend_link):
        try:
            os.symlink("../../novel_generator.db", backend_link)
            print(f"✅ 创建符号链接: {backend_link}")
        except Exception as e:
            print(f"❌ 创建符号链接失败: {e}")
    
    print("\n=== 数据库统一完成 ===")
    print(f"统一数据库路径: {os.path.abspath(unified_db_path)}")
    print("所有服务现在将使用同一个数据库文件")
    
    return True

if __name__ == "__main__":
    success = unify_database()
    if success:
        print("\n🎉 数据库统一成功！")
        print("请重启后端服务以使配置生效")
    else:
        print("\n❌ 数据库统一失败！")
