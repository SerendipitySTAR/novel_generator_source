"""
统一异常处理模块
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger("novel_generator.exceptions")


class NovelGeneratorException(Exception):
    """小说生成器基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(NovelGeneratorException):
    """数据验证异常"""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details or {}
        )
        if field:
            self.details["field"] = field


class ResourceNotFoundError(NovelGeneratorException):
    """资源未找到异常"""
    
    def __init__(self, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None):
        message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=details or {}
        )
        self.details.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })


class BusinessLogicError(NovelGeneratorException):
    """业务逻辑异常"""
    
    def __init__(self, message: str, operation: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details or {}
        )
        if operation:
            self.details["operation"] = operation


class ExternalServiceError(NovelGeneratorException):
    """外部服务异常"""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details or {}
        )
        self.details["service"] = service


class DatabaseError(NovelGeneratorException):
    """数据库异常"""
    
    def __init__(self, message: str, operation: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details or {}
        )
        if operation:
            self.details["operation"] = operation


class AIGenerationError(NovelGeneratorException):
    """AI生成异常"""
    
    def __init__(self, message: str, agent_type: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AI_GENERATION_ERROR",
            details=details or {}
        )
        if agent_type:
            self.details["agent_type"] = agent_type


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = "GENERAL_ERROR",
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    创建标准化的错误响应
    
    Args:
        status_code: HTTP状态码
        message: 错误消息
        error_code: 错误代码
        details: 错误详情
        
    Returns:
        JSONResponse: 标准化的错误响应
    """
    error_response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        }
    }
    
    logger.error(
        "Error response created",
        status_code=status_code,
        error_code=error_code,
        message=message,
        details=details
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def novel_generator_exception_handler(request: Request, exc: NovelGeneratorException) -> JSONResponse:
    """
    小说生成器自定义异常处理器
    """
    # 根据异常类型确定HTTP状态码
    status_code_map = {
        "VALIDATION_ERROR": 400,
        "RESOURCE_NOT_FOUND": 404,
        "BUSINESS_LOGIC_ERROR": 422,
        "EXTERNAL_SERVICE_ERROR": 502,
        "DATABASE_ERROR": 500,
        "AI_GENERATION_ERROR": 500,
        "GENERAL_ERROR": 500
    }
    
    status_code = status_code_map.get(exc.error_code, 500)
    
    return create_error_response(
        status_code=status_code,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP异常处理器
    """
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        error_code="HTTP_ERROR"
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    """
    logger.error(
        "Unhandled exception occurred",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        request_url=str(request.url),
        request_method=request.method,
        exc_info=True
    )
    
    return create_error_response(
        status_code=500,
        message="Internal server error occurred",
        error_code="INTERNAL_SERVER_ERROR",
        details={
            "exception_type": type(exc).__name__
        }
    )


def setup_exception_handlers(app):
    """
    设置异常处理器
    
    Args:
        app: FastAPI应用实例
    """
    app.add_exception_handler(NovelGeneratorException, novel_generator_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers configured")


# 异常处理装饰器
def handle_exceptions(default_message: str = "Operation failed"):
    """
    异常处理装饰器
    
    Args:
        default_message: 默认错误消息
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except NovelGeneratorException:
                # 重新抛出自定义异常
                raise
            except Exception as e:
                logger.error(
                    "Unexpected error in function",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True
                )
                raise NovelGeneratorException(
                    message=default_message,
                    error_code="UNEXPECTED_ERROR",
                    details={
                        "function": func.__name__,
                        "original_error": str(e),
                        "error_type": type(e).__name__
                    }
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except NovelGeneratorException:
                # 重新抛出自定义异常
                raise
            except Exception as e:
                logger.error(
                    "Unexpected error in function",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True
                )
                raise NovelGeneratorException(
                    message=default_message,
                    error_code="UNEXPECTED_ERROR",
                    details={
                        "function": func.__name__,
                        "original_error": str(e),
                        "error_type": type(e).__name__
                    }
                )
        
        # 检查是否是异步函数
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
