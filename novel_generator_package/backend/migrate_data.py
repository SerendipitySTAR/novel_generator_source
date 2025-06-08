#!/usr/bin/env python3
"""
数据迁移脚本：将backend目录下的章节数据迁移到根目录数据库
"""
import sqlite3
import os
import sys

def migrate_chapter_data():
    """迁移章节数据"""
    
    # 源数据库（backend目录）
    backend_db_path = "./novel_generator.db"
    # 目标数据库（根目录）
    root_db_path = "../../novel_generator.db"
    
    if not os.path.exists(backend_db_path):
        print(f"源数据库不存在: {backend_db_path}")
        return False
        
    if not os.path.exists(root_db_path):
        print(f"目标数据库不存在: {root_db_path}")
        return False
    
    try:
        # 连接源数据库
        source_conn = sqlite3.connect(backend_db_path)
        source_cursor = source_conn.cursor()
        
        # 连接目标数据库
        target_conn = sqlite3.connect(root_db_path)
        target_cursor = target_conn.cursor()
        
        # 查询源数据库中的章节
        source_cursor.execute("""
            SELECT project_id, id, chapter_number, title, content, 
                   status, quality_score, evaluation_result, 
                   created_at, updated_at
            FROM chapters
        """)
        chapters = source_cursor.fetchall()
        
        print(f"找到 {len(chapters)} 个章节需要迁移")
        
        # 查询目标数据库中的项目，建立ID映射
        target_cursor.execute("SELECT id, title FROM projects")
        target_projects = {title: id for id, title in target_cursor.fetchall()}
        
        print("目标数据库中的项目:")
        for title, id in target_projects.items():
            print(f"  {title}: {id}")
        
        migrated_count = 0
        
        for chapter in chapters:
            (source_project_id, chapter_id, chapter_number, title, content, 
             status, quality_score, evaluation_result, created_at, updated_at) = chapter
            
            # 查询源项目信息
            source_cursor.execute("SELECT title FROM projects WHERE id = ?", (source_project_id,))
            source_project = source_cursor.fetchone()
            
            if not source_project:
                print(f"跳过章节 {chapter_id}：找不到源项目 {source_project_id}")
                continue
                
            source_project_title = source_project[0]
            
            # 查找目标项目ID
            target_project_id = target_projects.get(source_project_title)
            if not target_project_id:
                print(f"跳过章节 {chapter_id}：目标数据库中找不到项目 '{source_project_title}'")
                continue
            
            # 检查目标数据库中是否已存在该章节
            target_cursor.execute("""
                SELECT id FROM chapters 
                WHERE project_id = ? AND chapter_number = ?
            """, (target_project_id, chapter_number))
            
            existing_chapter = target_cursor.fetchone()
            if existing_chapter:
                print(f"跳过章节 {chapter_id}：目标数据库中已存在第{chapter_number}章")
                continue
            
            # 插入章节到目标数据库
            target_cursor.execute("""
                INSERT INTO chapters (
                    id, project_id, chapter_number, title, content,
                    status, quality_score, evaluation_result,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chapter_id, target_project_id, chapter_number, title, content,
                status, quality_score, evaluation_result, created_at, updated_at
            ))
            
            migrated_count += 1
            print(f"迁移章节: {title} (第{chapter_number}章) -> 项目 {source_project_title}")
        
        # 提交更改
        target_conn.commit()
        
        print(f"\n迁移完成！成功迁移 {migrated_count} 个章节")
        
        # 关闭连接
        source_conn.close()
        target_conn.close()
        
        return True
        
    except Exception as e:
        print(f"迁移失败: {e}")
        return False

if __name__ == "__main__":
    print("开始数据迁移...")
    success = migrate_chapter_data()
    if success:
        print("数据迁移成功！")
        sys.exit(0)
    else:
        print("数据迁移失败！")
        sys.exit(1)
