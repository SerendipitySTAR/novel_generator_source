"""
API路由初始化文件
"""
from fastapi import APIRouter

router = APIRouter()

# 导入各模块路由
from app.api.projects import router as projects_router
from app.api.concepts import router as concepts_router
from app.api.world_settings import router as world_settings_router
from app.api.plot_outlines import router as plot_outlines_router
from app.api.characters import router as characters_router
from app.api.chapters import router as chapters_router

# 注册路由
router.include_router(projects_router, prefix="/projects", tags=["projects"])
router.include_router(concepts_router, prefix="/projects/{project_id}/concepts", tags=["concepts"])
router.include_router(world_settings_router, prefix="/projects/{project_id}/world-settings", tags=["world_settings"])
router.include_router(plot_outlines_router, prefix="/projects/{project_id}/plot-outlines", tags=["plot_outlines"])
router.include_router(characters_router, prefix="/projects/{project_id}/characters", tags=["characters"])
router.include_router(chapters_router, prefix="/projects/{project_id}/chapters", tags=["chapters"])
