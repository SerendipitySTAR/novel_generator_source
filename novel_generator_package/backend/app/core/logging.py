"""
统一日志配置模块
"""
import logging
import sys
from pathlib import Path
from typing import Optional
import structlog
from structlog.stdlib import LoggerFactory
from app.config import settings


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_json: bool = False
) -> None:
    """
    设置结构化日志配置
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        enable_json: 是否启用JSON格式输出
    """
    # 配置标准库日志
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # 配置structlog处理器
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # 配置structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        if enable_json:
            file_formatter = logging.Formatter('%(message)s')
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    获取结构化日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        structlog.stdlib.BoundLogger: 日志记录器实例
    """
    return structlog.get_logger(name)


# 应用级别的日志记录器
app_logger = get_logger("novel_generator")
api_logger = get_logger("novel_generator.api")
agent_logger = get_logger("novel_generator.agents")
db_logger = get_logger("novel_generator.database")


class LoggerMixin:
    """日志记录器混入类"""
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """获取当前类的日志记录器"""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


# 日志装饰器
def log_function_call(logger: Optional[structlog.stdlib.BoundLogger] = None):
    """
    记录函数调用的装饰器
    
    Args:
        logger: 可选的日志记录器，如果不提供则使用默认的app_logger
    """
    def decorator(func):
        import functools
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            log = logger or app_logger
            log.info(
                "Function called",
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            try:
                result = await func(*args, **kwargs)
                log.info("Function completed successfully", function=func.__name__)
                return result
            except Exception as e:
                log.error(
                    "Function failed",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            log = logger or app_logger
            log.info(
                "Function called",
                function=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            try:
                result = func(*args, **kwargs)
                log.info("Function completed successfully", function=func.__name__)
                return result
            except Exception as e:
                log.error(
                    "Function failed",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise
        
        # 检查是否是异步函数
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# 初始化日志系统
def init_logging():
    """初始化应用日志系统"""
    log_level = "DEBUG" if settings.DEBUG else "INFO"
    log_file = "logs/novel_generator.log" if not settings.DEBUG else None
    
    setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_json=not settings.DEBUG
    )
    
    app_logger.info(
        "Logging system initialized",
        log_level=log_level,
        debug_mode=settings.DEBUG,
        log_file=log_file
    )
