"""
安全认证模块
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.config import settings
from app.core.logging import get_logger

logger = get_logger("novel_generator.security")

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTP Bearer认证
security = HTTPBearer(auto_error=False)


class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[str] = None
    username: Optional[str] = None


class User(BaseModel):
    """用户模型"""
    id: str
    username: str
    email: Optional[str] = None
    is_active: bool = True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希密码
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info("Access token created", user_id=data.get("sub"), expires_at=expire)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    验证令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Optional[TokenData]: 令牌数据，验证失败返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None:
            return None
            
        token_data = TokenData(user_id=user_id, username=username)
        logger.debug("Token verified successfully", user_id=user_id)
        
        return token_data
        
    except JWTError as e:
        logger.warning("Token verification failed", error=str(e))
        return None


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[User]:
    """
    获取当前用户（可选认证）
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        Optional[User]: 当前用户，未认证时返回None
    """
    if not credentials:
        return None
    
    token_data = verify_token(credentials.credentials)
    if not token_data:
        return None
    
    # 这里应该从数据库获取用户信息
    # 目前返回模拟用户
    user = User(
        id=token_data.user_id,
        username=token_data.username or "anonymous"
    )
    
    logger.debug("Current user retrieved", user_id=user.id, username=user.username)
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户（必须认证）
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前活跃用户
        
    Raises:
        HTTPException: 未认证或用户不活跃
    """
    if not current_user:
        logger.warning("Authentication required but no user provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        logger.warning("Inactive user attempted access", user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    认证用户
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        Optional[User]: 认证成功返回用户，失败返回None
    """
    # 这里应该从数据库验证用户
    # 目前返回模拟认证
    
    # 模拟用户数据
    fake_users = {
        "admin": {
            "id": "1",
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True
        }
    }
    
    user_data = fake_users.get(username)
    if not user_data:
        logger.warning("User not found", username=username)
        return None
    
    if not verify_password(password, user_data["hashed_password"]):
        logger.warning("Invalid password", username=username)
        return None
    
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        is_active=user_data["is_active"]
    )
    
    logger.info("User authenticated successfully", user_id=user.id, username=username)
    return user


def create_user_token(user: User) -> Token:
    """
    为用户创建令牌
    
    Args:
        user: 用户对象
        
    Returns:
        Token: 访问令牌
    """
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


# 输入验证和清理
def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    清理和验证输入文本
    
    Args:
        text: 输入文本
        max_length: 最大长度
        
    Returns:
        str: 清理后的文本
        
    Raises:
        ValueError: 输入无效
    """
    if not text or not isinstance(text, str):
        raise ValueError("输入文本不能为空")
    
    # 移除潜在的危险字符
    cleaned_text = text.strip()
    
    # 检查长度
    if len(cleaned_text) > max_length:
        raise ValueError(f"输入文本长度不能超过 {max_length} 字符")
    
    # 检查是否包含恶意内容（简单示例）
    dangerous_patterns = ["<script", "javascript:", "data:"]
    for pattern in dangerous_patterns:
        if pattern.lower() in cleaned_text.lower():
            logger.warning("Potentially dangerous input detected", pattern=pattern)
            raise ValueError("输入包含不安全内容")
    
    return cleaned_text


def validate_project_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证项目数据
    
    Args:
        data: 项目数据
        
    Returns:
        Dict[str, Any]: 验证后的数据
        
    Raises:
        ValueError: 数据无效
    """
    required_fields = ["title"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"缺少必需字段: {field}")
    
    # 清理文本字段
    text_fields = ["title", "description"]
    for field in text_fields:
        if field in data and data[field]:
            data[field] = sanitize_input(data[field])
    
    return data


# 权限检查装饰器
def require_auth(func):
    """
    需要认证的装饰器
    """
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # 检查是否有current_user参数
        if 'current_user' in kwargs:
            user = kwargs['current_user']
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
        
        return await func(*args, **kwargs)
    
    return wrapper


# 速率限制（简单实现）
class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int = 100, window: int = 3600) -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限制键（如IP地址）
            limit: 限制次数
            window: 时间窗口（秒）
            
        Returns:
            bool: 是否允许
        """
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # 清理过期请求
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).total_seconds() < window
        ]
        
        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            logger.warning("Rate limit exceeded", key=key, count=len(self.requests[key]))
            return False
        
        # 记录当前请求
        self.requests[key].append(now)
        return True


# 全局速率限制器实例
rate_limiter = RateLimiter()
