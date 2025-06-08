"""
应用入口文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.db import init_db
from app.core.logging import init_logging, get_logger
from app.core.exceptions import setup_exception_handlers

# 初始化日志系统
init_logging()
logger = get_logger("novel_generator.main")

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

logger.info("FastAPI application created", app_name=settings.APP_NAME)

# 初始化数据库
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error("Failed to initialize database", error=str(e))
    raise

# 设置异常处理器
setup_exception_handlers(app)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

# 项目状态存储已迁移到数据库，移除内存存储

# 导入路由
from app.api.settings import router as settings_router
from app.api.new_routes import router as new_routes_router

# 注册路由 - 只保留新版API
app.include_router(new_routes_router, prefix=settings.API_PREFIX, tags=["novel-generator"])
app.include_router(settings_router, prefix=f"{settings.API_PREFIX}/settings", tags=["settings"])

logger.info("API routes registered")

# 挂载静态文件
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    """
    根路由，返回应用信息
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION
    }

# 异常处理器已在setup_exception_handlers中配置

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
