"""
项目API测试
"""
import pytest
from fastapi.testclient import TestClient


class TestProjectsAPI:
    """项目API测试类"""
    
    def test_create_project_success(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试成功创建项目"""
        response = client.post("/api/v1/projects", json=sample_project_data)
        
        assert response.status_code == 201
        data = response.json()
        
        test_helpers.assert_success_response(data, "项目创建成功")
        
        project = data["data"]
        assert project["title"] == sample_project_data["title"]
        assert project["description"] == sample_project_data["description"]
        assert project["target_chapters"] == sample_project_data["target_chapters"]
        assert "id" in project
        assert "created_at" in project
    
    def test_create_project_missing_title(self, client: TestClient):
        """测试创建项目时缺少标题"""
        project_data = {
            "description": "测试描述"
        }
        
        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_project_empty_title(self, client: TestClient):
        """测试创建项目时标题为空"""
        project_data = {
            "title": "",
            "description": "测试描述"
        }
        
        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 400
        
        data = response.json()
        assert data["success"] is False
        assert "VALIDATION_ERROR" in data["error"]["code"]
    
    def test_get_project_success(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试成功获取项目"""
        # 先创建项目
        project = test_helpers.create_test_project(client, sample_project_data)
        project_id = project["id"]
        
        # 获取项目
        response = client.get(f"/api/v1/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        test_helpers.assert_success_response(data, "项目详情获取成功")
        
        retrieved_project = data["data"]
        assert retrieved_project["id"] == project_id
        assert retrieved_project["title"] == sample_project_data["title"]
    
    def test_get_project_not_found(self, client: TestClient):
        """测试获取不存在的项目"""
        response = client.get("/api/v1/projects/nonexistent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "RESOURCE_NOT_FOUND" in data["error"]["code"]
    
    def test_update_project_success(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试成功更新项目"""
        # 先创建项目
        project = test_helpers.create_test_project(client, sample_project_data)
        project_id = project["id"]
        
        # 更新项目
        update_data = {
            "title": "更新后的标题",
            "description": "更新后的描述"
        }
        
        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        test_helpers.assert_success_response(data, "项目更新成功")
        
        updated_project = data["data"]
        assert updated_project["title"] == update_data["title"]
        assert updated_project["description"] == update_data["description"]
    
    def test_update_project_partial(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试部分更新项目"""
        # 先创建项目
        project = test_helpers.create_test_project(client, sample_project_data)
        project_id = project["id"]
        
        # 只更新标题
        update_data = {
            "title": "只更新标题"
        }
        
        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        
        updated_project = data["data"]
        assert updated_project["title"] == update_data["title"]
        # 描述应该保持不变
        assert updated_project["description"] == sample_project_data["description"]
    
    def test_delete_project_success(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试成功删除项目"""
        # 先创建项目
        project = test_helpers.create_test_project(client, sample_project_data)
        project_id = project["id"]
        
        # 删除项目
        response = client.delete(f"/api/v1/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        test_helpers.assert_success_response(data, "项目删除成功")
        
        # 验证项目已被删除
        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == 404
    
    def test_list_projects_empty(self, client: TestClient):
        """测试获取空项目列表"""
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"] == []
        assert "meta" in data
        assert data["meta"]["pagination"]["total"] == 0
    
    def test_list_projects_with_data(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试获取包含数据的项目列表"""
        # 创建多个项目
        project1 = test_helpers.create_test_project(client, {
            **sample_project_data,
            "title": "项目1"
        })
        project2 = test_helpers.create_test_project(client, {
            **sample_project_data,
            "title": "项目2"
        })
        
        # 获取项目列表
        response = client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        projects = data["data"]
        assert len(projects) == 2
        
        # 验证分页信息
        pagination = data["meta"]["pagination"]
        assert pagination["total"] == 2
        assert pagination["page"] == 1
        assert pagination["page_size"] == 20
    
    def test_list_projects_pagination(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试项目列表分页"""
        # 创建多个项目
        for i in range(5):
            test_helpers.create_test_project(client, {
                **sample_project_data,
                "title": f"项目{i+1}"
            })
        
        # 测试第一页
        response = client.get("/api/v1/projects?page=1&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        
        projects = data["data"]
        assert len(projects) == 2
        
        pagination = data["meta"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 2
        assert pagination["total"] == 5
        assert pagination["total_pages"] == 3
        assert pagination["has_next"] is True
        assert pagination["has_prev"] is False
    
    def test_get_project_summary(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试获取项目摘要"""
        # 先创建项目
        project = test_helpers.create_test_project(client, sample_project_data)
        project_id = project["id"]
        
        # 获取项目摘要
        response = client.get(f"/api/v1/projects/{project_id}/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        test_helpers.assert_success_response(data, "项目摘要获取成功")
        
        summary = data["data"]
        assert "project" in summary
        assert "stats" in summary
        assert "progress" in summary
        
        # 验证统计信息
        stats = summary["stats"]
        assert "concepts_count" in stats
        assert "world_settings_count" in stats
        assert "plot_outlines_count" in stats
        assert "characters_count" in stats
        assert "chapters_count" in stats
    
    def test_update_project_status(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试更新项目状态"""
        # 先创建项目
        project = test_helpers.create_test_project(client, sample_project_data)
        project_id = project["id"]
        
        # 更新状态
        response = client.patch(f"/api/v1/projects/{project_id}/status?status=in_progress")
        
        assert response.status_code == 200
        data = response.json()
        
        test_helpers.assert_success_response(data)
        
        updated_project = data["data"]
        assert updated_project["status"] == "in_progress"
    
    def test_update_project_status_invalid(self, client: TestClient, sample_project_data: dict, test_helpers):
        """测试更新项目状态为无效值"""
        # 先创建项目
        project = test_helpers.create_test_project(client, sample_project_data)
        project_id = project["id"]
        
        # 更新为无效状态
        response = client.patch(f"/api/v1/projects/{project_id}/status?status=invalid_status")
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "VALIDATION_ERROR" in data["error"]["code"]
