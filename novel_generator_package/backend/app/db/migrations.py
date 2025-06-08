"""
数据库迁移脚本
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.core.logging import get_logger
from app.models.base import Base
from app.models import Project, Concept, WorldSetting, PlotOutline, Character, Chapter

logger = get_logger("novel_generator.migrations")


def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        if settings.DEBUG:
            # SQLite数据库会自动创建
            logger.info("Using SQLite database, will be created automatically")
            return
        
        # PostgreSQL需要先创建数据库
        from urllib.parse import urlparse
        parsed_url = urlparse(settings.DATABASE_URL)
        
        # 连接到默认数据库
        default_db_url = f"{parsed_url.scheme}://{parsed_url.username}:{parsed_url.password}@{parsed_url.hostname}:{parsed_url.port}/postgres"
        engine = create_engine(default_db_url)
        
        with engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": parsed_url.path[1:]})
            
            if not result.fetchone():
                # 创建数据库
                conn.execute(text("COMMIT"))
                conn.execute(text(f"CREATE DATABASE {parsed_url.path[1:]}"))
                logger.info("Database created", database=parsed_url.path[1:])
            else:
                logger.info("Database already exists", database=parsed_url.path[1:])
        
        engine.dispose()
        
    except Exception as e:
        logger.error("Failed to create database", error=str(e))
        raise


def run_migrations():
    """运行数据库迁移"""
    try:
        logger.info("Starting database migrations")
        
        # 确保数据库存在
        create_database_if_not_exists()
        
        # 创建引擎
        if settings.DEBUG:
            engine = create_engine(
                "sqlite:///../../novel_generator.db",
                connect_args={"check_same_thread": False}
            )
        else:
            engine = create_engine(settings.DATABASE_URL)
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database migrations completed successfully")
        
        # 运行数据迁移
        run_data_migrations(engine)
        
    except Exception as e:
        logger.error("Database migrations failed", error=str(e))
        raise


def run_data_migrations(engine):
    """运行数据迁移"""
    try:
        logger.info("Starting data migrations")
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # 检查是否需要迁移旧数据
            migrate_legacy_data(db)
            
            # 添加默认数据
            add_default_data(db)
            
            db.commit()
            logger.info("Data migrations completed successfully")
            
        except Exception as e:
            db.rollback()
            logger.error("Data migrations failed", error=str(e))
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error("Failed to run data migrations", error=str(e))
        raise


def migrate_legacy_data(db):
    """迁移旧数据"""
    try:
        # 这里可以添加从旧版本迁移数据的逻辑
        # 例如：从内存存储迁移到数据库
        
        logger.info("Checking for legacy data to migrate")
        
        # 检查是否存在旧的数据文件
        import os
        legacy_db_path = "../../novel_generator.db"
        
        if os.path.exists(legacy_db_path):
            logger.info("Found legacy database, migration may be needed")
            # 这里可以添加具体的迁移逻辑
        
        logger.info("Legacy data migration check completed")
        
    except Exception as e:
        logger.warning("Legacy data migration failed", error=str(e))
        # 不抛出异常，因为这不是关键操作


def add_default_data(db):
    """添加默认数据"""
    try:
        logger.info("Adding default data")
        
        # 检查是否已有数据
        existing_projects = db.query(Project).first()
        if existing_projects:
            logger.info("Default data already exists, skipping")
            return
        
        # 添加示例项目（可选）
        if settings.DEBUG:
            sample_project = Project(
                title="示例项目",
                description="这是一个示例项目，用于演示系统功能",
                status="draft",
                target_chapters=10,
                writing_style="详细生动",
                genre="科幻"
            )
            
            db.add(sample_project)
            db.flush()  # 获取ID
            
            # 添加示例概述
            sample_concept = Concept(
                project_id=sample_project.id,
                title="示例概述",
                content="这是一个关于未来世界的科幻故事...",
                is_selected=True
            )
            
            db.add(sample_concept)
            
            logger.info("Sample data added", project_id=sample_project.id)
        
        logger.info("Default data addition completed")
        
    except Exception as e:
        logger.error("Failed to add default data", error=str(e))
        raise


def check_database_health():
    """检查数据库健康状态"""
    try:
        logger.info("Checking database health")
        
        if settings.DEBUG:
            engine = create_engine(
                "sqlite:///../../novel_generator.db",
                connect_args={"check_same_thread": False}
            )
        else:
            engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # 执行简单查询
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
            logger.info("Database health check passed")
            return True
            
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False


def reset_database():
    """重置数据库（仅用于开发环境）"""
    if not settings.DEBUG:
        logger.error("Database reset is only allowed in debug mode")
        raise ValueError("Database reset is only allowed in debug mode")
    
    try:
        logger.warning("Resetting database - all data will be lost")
        
        if settings.DEBUG:
            engine = create_engine(
                "sqlite:///../../novel_generator.db",
                connect_args={"check_same_thread": False}
            )
        else:
            engine = create_engine(settings.DATABASE_URL)
        
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        
        # 重新创建表
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database reset completed")
        
        # 添加默认数据
        run_data_migrations(engine)
        
    except Exception as e:
        logger.error("Database reset failed", error=str(e))
        raise


if __name__ == "__main__":
    # 运行迁移
    run_migrations()
