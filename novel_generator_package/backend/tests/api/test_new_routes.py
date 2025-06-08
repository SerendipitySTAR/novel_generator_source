import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app # Assuming your FastAPI app instance is here
from app.api.new_routes import ChapterGenerateRequestV3 # Import the new request model
from app.agents.chapter_chronicler import ChapterChroniclerAgent
from app.db.repositories import ProjectRepository # For mocking project existence check
from app.db import get_db # For overriding dependency

# Mock database dependency for testing
# This is a simplified version. A more robust setup might use a test database.
mock_db_session_global = MagicMock(spec=Session)

async def override_get_db():
    return mock_db_session_global

app.dependency_overrides[get_db] = override_get_db


class TestNewRoutesChapters(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = TestClient(app)
        # Reset mocks for each test if necessary, especially for global mocks
        mock_db_session_global.reset_mock()

        # Mock the project existence check that happens in the route
        # This mock setup assumes ProjectRepository is directly used or can be patched this way.
        # If it's more complex, deeper patching or service layer mocking might be needed.
        self.project_repo_patch = patch('app.api.new_routes.ProjectRepository', autospec=True)
        self.MockProjectRepository = self.project_repo_patch.start()
        self.mock_project_repo_instance = self.MockProjectRepository.return_value
        self.mock_project_repo_instance.get_by_id.return_value = MagicMock() # Simulate project exists

        # We also need to mock the ChapterRepository for saving the chapter
        self.chapter_repo_patch = patch('app.api.new_routes.ChapterRepository', autospec=True)
        self.MockChapterRepository = self.chapter_repo_patch.start()
        self.mock_chapter_repo_instance = self.MockChapterRepository.return_value
        # Mock the create method to return a mock chapter object
        self.mock_db_chapter = MagicMock()
        self.mock_db_chapter.id = "chapter_test_id_123"
        self.mock_db_chapter.chapter_number = 1
        self.mock_db_chapter.title = "Test Chapter Title"
        self.mock_db_chapter.content = "Generated chapter content."
        self.mock_db_chapter.word_count = 4
        self.mock_db_chapter.writing_style = "test_style"
        self.mock_db_chapter.status = "draft"
        self.mock_db_chapter.created_at = "2023-01-01T12:00:00" # Isoformat string
        self.mock_db_chapter.updated_at = "2023-01-01T12:00:00"
        self.mock_chapter_repo_instance.create.return_value = self.mock_db_chapter


    def tearDown(self):
        self.project_repo_patch.stop()
        self.chapter_repo_patch.stop()
        app.dependency_overrides = {} # Clear overrides

    @patch('app.api.new_routes.ChapterChroniclerAgent', autospec=True)
    async def test_generate_chapter_endpoint_v3_params(self, MockChapterChroniclerAgent):
        # Mock the ChapterChroniclerAgent's run method
        mock_agent_instance = MockChapterChroniclerAgent.return_value
        mock_agent_instance.run = AsyncMock(return_value={
            "chapter_content": "Generated chapter content."
        })

        project_id = "test_project_id"

        request_payload = {
            "chapter_outline": {"number": 1, "title": "The Test Chapter"},
            "world_setting": {"description": "A world for testing."},
            "character_profiles": [{"name": "Test Character"}],
            "previous_summary": "Once upon a time...",
            "kb_context": [],
            "writing_style": "Clear and concise",
            # New V3 fields
            "novel_progress": 0.5,
            "tension_level": "medium",
            "chapter_type": "plot_development",
            "long_term_goals": ["Advance main quest", "Reveal subplot hint"]
        }

        response = self.client.post(f"/projects/{project_id}/chapters", json=request_payload)

        # Check response status
        self.assertEqual(response.status_code, 200) # Assuming 200 for success

        # Verify ChapterChroniclerAgent was instantiated (indirectly, by checking run call)
        # MockChapterChroniclerAgent.assert_called_once() # Needs llm and project_id

        # Verify ChapterChroniclerAgent.run was called with the correct input_data
        mock_agent_instance.run.assert_called_once()

        args, kwargs = mock_agent_instance.run.call_args
        called_input_data = args[0] # The input_data dict is the first positional arg

        self.assertEqual(called_input_data["mode"], "generate")
        self.assertEqual(called_input_data["chapter_outline"], request_payload["chapter_outline"])
        self.assertEqual(called_input_data["world_setting"], request_payload["world_setting"])
        self.assertEqual(called_input_data["character_profiles"], request_payload["character_profiles"])
        self.assertEqual(called_input_data["previous_summary"], request_payload["previous_summary"])
        self.assertEqual(called_input_data["writing_style"], request_payload["writing_style"])

        # Assert new V3 parameters
        self.assertEqual(called_input_data["novel_progress"], request_payload["novel_progress"])
        self.assertEqual(called_input_data["tension_level"], request_payload["tension_level"])
        self.assertEqual(called_input_data["chapter_type"], request_payload["chapter_type"])
        self.assertEqual(called_input_data["long_term_goals"], request_payload["long_term_goals"])

        # Check some parts of the response body
        response_json = response.json()
        self.assertEqual(response_json["title"], request_payload["chapter_outline"]["title"])
        self.assertEqual(response_json["content"], "Generated chapter content.")


if __name__ == '__main__':
    # This is unusual for FastAPI/pytest tests but okay for pure unittest style
    unittest.main()
