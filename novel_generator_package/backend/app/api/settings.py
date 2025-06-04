"""
设置相关API路由
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
from app.config import settings

router = APIRouter()

@router.get("/token-config", response_model=Dict[str, Any])
async def get_token_config():
    """
    获取当前的Token配置
    """
    return {
        "concept_max_tokens": settings.CONCEPT_MAX_TOKENS,
        "concept_expand_max_tokens": settings.CONCEPT_EXPAND_MAX_TOKENS,
        "world_setting_max_tokens": settings.WORLD_SETTING_MAX_TOKENS,
        "plot_outline_max_tokens": settings.PLOT_OUTLINE_MAX_TOKENS,
        "character_max_tokens": settings.CHARACTER_MAX_TOKENS,
        "chapter_max_tokens": settings.CHAPTER_MAX_TOKENS,
        "chapter_polish_max_tokens": settings.CHAPTER_POLISH_MAX_TOKENS,
        "plot_branches_max_tokens": settings.PLOT_BRANCHES_MAX_TOKENS,
        "agent_temperature": settings.AGENT_TEMPERATURE,
        "agent_top_p": settings.AGENT_TOP_P,
        "default_chapter_length": settings.DEFAULT_CHAPTER_LENGTH
    }

@router.post("/token-config", response_model=Dict[str, Any])
async def update_token_config(config: Dict[str, Any] = Body(...)):
    """
    更新Token配置
    """
    # 验证配置值
    valid_keys = {
        "concept_max_tokens": (1000, 20000),
        "concept_expand_max_tokens": (2000, 20000),
        "world_setting_max_tokens": (2000, 20000),
        "plot_outline_max_tokens": (3000, 30000),
        "character_max_tokens": (2000, 20000),
        "chapter_max_tokens": (2000, 20000),
        "chapter_polish_max_tokens": (2000, 20000),
        "plot_branches_max_tokens": (1000, 10000),
        "agent_temperature": (0.1, 2.0),
        "agent_top_p": (0.1, 1.0),
        "default_chapter_length": (1000, 10000)
    }
    
    updated_config = {}
    
    for key, value in config.items():
        if key in valid_keys:
            min_val, max_val = valid_keys[key]
            if min_val <= value <= max_val:
                # 动态更新settings对象
                setattr(settings, key.upper(), value)
                updated_config[key] = value
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"{key} 值必须在 {min_val} 到 {max_val} 之间"
                )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的配置项: {key}"
            )
    
    return {
        "message": "配置更新成功",
        "updated_config": updated_config
    }

@router.get("/writing-styles", response_model=List[str])
async def get_writing_styles():
    """
    获取可用的写作风格列表
    """
    return settings.WRITING_STYLES

@router.post("/writing-styles", response_model=Dict[str, Any])
async def add_writing_style(style_data: Dict[str, str] = Body(...)):
    """
    添加自定义写作风格
    """
    style_name = style_data.get("name", "").strip()
    
    if not style_name:
        raise HTTPException(status_code=400, detail="写作风格名称不能为空")
    
    if style_name in settings.WRITING_STYLES:
        raise HTTPException(status_code=400, detail="该写作风格已存在")
    
    # 添加到写作风格列表（在实际应用中应该持久化到数据库）
    if "自定义" in settings.WRITING_STYLES:
        # 在"自定义"之前插入
        index = settings.WRITING_STYLES.index("自定义")
        settings.WRITING_STYLES.insert(index, style_name)
    else:
        settings.WRITING_STYLES.append(style_name)
    
    return {
        "message": "写作风格添加成功",
        "style_name": style_name,
        "all_styles": settings.WRITING_STYLES
    }

@router.delete("/writing-styles/{style_name}", response_model=Dict[str, Any])
async def remove_writing_style(style_name: str):
    """
    删除自定义写作风格
    """
    # 不允许删除预设的写作风格
    default_styles = [
        "详细生动", "简洁明快", "诗意抒情", "悬疑紧张", "幽默风趣",
        "古典优雅", "现代都市", "科幻硬核", "奇幻史诗", "自定义"
    ]
    
    if style_name in default_styles:
        raise HTTPException(status_code=400, detail="不能删除预设的写作风格")
    
    if style_name not in settings.WRITING_STYLES:
        raise HTTPException(status_code=404, detail="写作风格不存在")
    
    settings.WRITING_STYLES.remove(style_name)
    
    return {
        "message": "写作风格删除成功",
        "removed_style": style_name,
        "all_styles": settings.WRITING_STYLES
    }

@router.get("/system-info", response_model=Dict[str, Any])
async def get_system_info():
    """
    获取系统信息
    """
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "app_description": settings.APP_DESCRIPTION,
        "llm_model": settings.DEFAULT_LLM_MODEL,
        "api_base": settings.OPENAI_API_BASE,
        "quality_threshold": settings.QUALITY_THRESHOLD,
        "max_retries": settings.MAX_RETRIES
    }
