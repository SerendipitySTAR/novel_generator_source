"""
项目启动脚本
"""
import os
import sys
import uvicorn

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.config import settings

if __name__ == "__main__":
    print(f"启动自动小说生成器API服务，访问地址: http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
