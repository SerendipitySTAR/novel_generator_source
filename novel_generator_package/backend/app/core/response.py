"""
统一API响应格式
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger("novel_generator.response")


class APIResponse(BaseModel):
    """标准API响应模型"""
    success: bool
    message: str
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None
    meta: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


def create_success_response(
    data: Optional[Union[Dict[str, Any], List[Any], Any]] = None,
    message: str = "Operation completed successfully",
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200
) -> JSONResponse:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        meta: 元数据
        status_code: HTTP状态码
        
    Returns:
        JSONResponse: 标准化的成功响应
    """
    response_data = APIResponse(
        success=True,
        message=message,
        data=data,
        meta=meta
    )
    
    logger.debug(
        "Success response created",
        status_code=status_code,
        message=message,
        has_data=data is not None,
        has_meta=meta is not None
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response_data.model_dump(exclude_none=True)
    )


def create_paginated_response(
    items: List[Any],
    page: int,
    page_size: int,
    total: int,
    message: str = "Data retrieved successfully"
) -> JSONResponse:
    """
    创建分页响应
    
    Args:
        items: 数据项列表
        page: 当前页码
        page_size: 每页大小
        total: 总数量
        message: 响应消息
        
    Returns:
        JSONResponse: 分页响应
    """
    total_pages = (total + page_size - 1) // page_size
    
    pagination_meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
    
    return create_success_response(
        data=items,
        message=message,
        meta={"pagination": pagination_meta.model_dump()}
    )


def create_created_response(
    data: Union[Dict[str, Any], Any],
    message: str = "Resource created successfully"
) -> JSONResponse:
    """
    创建资源创建成功响应
    
    Args:
        data: 创建的资源数据
        message: 响应消息
        
    Returns:
        JSONResponse: 201状态码的成功响应
    """
    return create_success_response(
        data=data,
        message=message,
        status_code=201
    )


def create_updated_response(
    data: Union[Dict[str, Any], Any],
    message: str = "Resource updated successfully"
) -> JSONResponse:
    """
    创建资源更新成功响应
    
    Args:
        data: 更新后的资源数据
        message: 响应消息
        
    Returns:
        JSONResponse: 成功响应
    """
    return create_success_response(
        data=data,
        message=message
    )


def create_deleted_response(
    message: str = "Resource deleted successfully"
) -> JSONResponse:
    """
    创建资源删除成功响应
    
    Args:
        message: 响应消息
        
    Returns:
        JSONResponse: 成功响应
    """
    return create_success_response(
        message=message,
        status_code=204
    )


def create_no_content_response() -> JSONResponse:
    """
    创建无内容响应
    
    Returns:
        JSONResponse: 204状态码响应
    """
    return JSONResponse(status_code=204)


# 响应装饰器
def api_response(
    success_message: str = "Operation completed successfully",
    created_message: str = "Resource created successfully",
    updated_message: str = "Resource updated successfully"
):
    """
    API响应装饰器，自动包装返回值为标准响应格式
    
    Args:
        success_message: 成功消息
        created_message: 创建成功消息
        updated_message: 更新成功消息
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                
                # 如果返回值已经是JSONResponse，直接返回
                if isinstance(result, JSONResponse):
                    return result
                
                # 根据函数名判断操作类型
                if "create" in func.__name__:
                    return create_created_response(result, created_message)
                elif "update" in func.__name__:
                    return create_updated_response(result, updated_message)
                elif "delete" in func.__name__:
                    return create_deleted_response()
                else:
                    return create_success_response(result, success_message)
                    
            except Exception as e:
                # 让异常处理器处理
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # 如果返回值已经是JSONResponse，直接返回
                if isinstance(result, JSONResponse):
                    return result
                
                # 根据函数名判断操作类型
                if "create" in func.__name__:
                    return create_created_response(result, created_message)
                elif "update" in func.__name__:
                    return create_updated_response(result, updated_message)
                elif "delete" in func.__name__:
                    return create_deleted_response()
                else:
                    return create_success_response(result, success_message)
                    
            except Exception as e:
                # 让异常处理器处理
                raise
        
        # 检查是否是异步函数
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 常用响应模板
class ResponseTemplates:
    """常用响应模板"""
    
    @staticmethod
    def project_created(project_data: Dict[str, Any]) -> JSONResponse:
        """项目创建成功响应"""
        return create_created_response(
            data=project_data,
            message="项目创建成功"
        )
    
    @staticmethod
    def concept_generated(concepts: List[Dict[str, Any]]) -> JSONResponse:
        """概述生成成功响应"""
        return create_success_response(
            data={"concepts": concepts},
            message=f"成功生成 {len(concepts)} 个概述"
        )
    
    @staticmethod
    def world_setting_generated(world_settings: List[Dict[str, Any]]) -> JSONResponse:
        """世界观设定生成成功响应"""
        return create_success_response(
            data={"world_settings": world_settings},
            message=f"成功生成 {len(world_settings)} 个世界观设定"
        )
    
    @staticmethod
    def plot_outline_generated(plot_outlines: List[Dict[str, Any]]) -> JSONResponse:
        """大纲生成成功响应"""
        return create_success_response(
            data={"plot_outlines": plot_outlines},
            message=f"成功生成 {len(plot_outlines)} 个大纲"
        )
    
    @staticmethod
    def character_generated(characters: List[Dict[str, Any]]) -> JSONResponse:
        """人物设定生成成功响应"""
        return create_success_response(
            data={"characters": characters},
            message=f"成功生成 {len(characters)} 个人物设定"
        )
    
    @staticmethod
    def chapter_generated(chapter_data: Dict[str, Any]) -> JSONResponse:
        """章节生成成功响应"""
        return create_success_response(
            data=chapter_data,
            message="章节生成成功"
        )
    
    @staticmethod
    def health_check() -> JSONResponse:
        """健康检查响应"""
        return create_success_response(
            data={
                "status": "healthy",
                "service": "小说生成器API"
            },
            message="服务运行正常"
        )
