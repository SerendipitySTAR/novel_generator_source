"""
测试配置文件
"""
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db
from app.models.base import Base
from app.core.logging import init_logging


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 创建会话
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 清理表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """设置测试日志"""
    init_logging()


@pytest.fixture
def sample_project_data():
    """示例项目数据"""
    return {
        "title": "测试项目",
        "description": "这是一个测试项目",
        "target_chapters": 5,
        "writing_style": "详细生动",
        "genre": "科幻"
    }


@pytest.fixture
def sample_concept_data():
    """示例概述数据"""
    return {
        "user_input": "一个关于时间旅行的科幻故事",
        "num_concepts": 2
    }


@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    return {
        "concepts": [
            "概述1：主角发现了时间旅行的秘密...",
            "概述2：在未来世界中，时间旅行成为了一种常见的交通方式..."
        ]
    }


# 测试工具函数
class TestHelpers:
    """测试辅助工具"""
    
    @staticmethod
    def create_test_project(client: TestClient, project_data: dict = None):
        """创建测试项目"""
        if project_data is None:
            project_data = {
                "title": "测试项目",
                "description": "测试描述",
                "target_chapters": 5,
                "writing_style": "详细生动",
                "genre": "科幻"
            }
        
        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 201
        return response.json()["data"]
    
    @staticmethod
    def create_test_concept(client: TestClient, project_id: str, concept_data: dict = None):
        """创建测试概述"""
        if concept_data is None:
            concept_data = {
                "user_input": "测试输入",
                "num_concepts": 1
            }
        
        response = client.post(f"/api/v1/projects/{project_id}/concepts", json=concept_data)
        return response.json()
    
    @staticmethod
    def assert_success_response(response_data: dict, expected_message: str = None):
        """断言成功响应"""
        assert response_data["success"] is True
        if expected_message:
            assert expected_message in response_data["message"]
        assert "data" in response_data
    
    @staticmethod
    def assert_error_response(response_data: dict, expected_error_code: str = None):
        """断言错误响应"""
        assert response_data["success"] is False
        assert "error" in response_data
        if expected_error_code:
            assert response_data["error"]["code"] == expected_error_code


@pytest.fixture
def test_helpers():
    """测试辅助工具实例"""
    return TestHelpers
