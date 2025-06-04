"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.config import settings
from app.models.base import Base

# 根据环境选择数据库
if settings.DEBUG:
    # 开发环境使用SQLite
    DATABASE_URL = "sqlite:///./novel_generator.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True  # 开发环境显示SQL语句
    )
else:
    # 生产环境使用PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    # 导入所有模型以确保它们被注册
    from app.models import (
        Project, Concept, WorldSetting, 
        PlotOutline, Character, Chapter
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
