import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.novel_generation_service import NovelGenerationService
from app.models import Chapter, WorldSetting, Character # Assuming these are your SQLAlchemy models

# Mock DB session if needed by service, or patch repositories directly
mock_db_session = MagicMock()

class TestNovelGenerationService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mocking the full DB session passed to service, or individual repositories
        self.service = NovelGenerationService(db=mock_db_session)
        # Mock LLM if service initializes it and passes to agents (it does)
        self.service.llm = AsyncMock()


    @patch('app.services.novel_generation_service.ContextSynthesizerAgent', autospec=True)
    async def test_get_previous_summary_integration_and_formatting(self, MockContextSynthesizerAgent):
        # Mock the ContextSynthesizerAgent's run method
        mock_context_agent_instance = MockContextSynthesizerAgent.return_value
        mock_context_agent_instance.run = AsyncMock(return_value={
            "long_term_summary": "Service: Mocked Long Term Summary.",
            "medium_summary": "Service: Mocked Medium Term Summary.",
            "recent_summary": "Service: Mocked Recent Summary.",
            "summary": "Service: Mocked Overall Comprehensive Summary."
        })

        # Mock repository calls
        mock_chapter_1 = MagicMock(spec=Chapter)
        mock_chapter_1.chapter_number = 1
        mock_chapter_1.title = "The First Step"
        mock_chapter_1.content = "Content of the first chapter."

        mock_chapter_2 = MagicMock(spec=Chapter)
        mock_chapter_2.chapter_number = 2
        mock_chapter_2.title = "The Second Step"
        mock_chapter_2.content = "Content of the second chapter."

        self.service.chapter_repo.get_by_project_id = MagicMock(return_value=[mock_chapter_1, mock_chapter_2])

        mock_ws_model = MagicMock(spec=WorldSetting)
        mock_ws_model.content = {"description": "A service-mocked world."}
        self.service.world_setting_repo.get_selected_by_project_id = MagicMock(return_value=mock_ws_model)

        mock_char_model = MagicMock(spec=Character)
        mock_char_model.content = [{"name": "Service Mock Character"}]
        self.service.character_repo.get_selected_by_project_id = MagicMock(return_value=[mock_char_model])

        project_id = "test_project_id"
        current_chapter_number = 3 # We want summary for chapter 3, so previous are 1 and 2

        formatted_summary = await self.service._get_previous_summary(project_id, current_chapter_number)

        # Verify ContextSynthesizerAgent was instantiated correctly (with the service's LLM)
        MockContextSynthesizerAgent.assert_called_once_with(llm=self.service.llm)

        # Verify ContextSynthesizerAgent.run was called with correct data
        expected_chapters_data = [
            {"chapter_number": 1, "title": "The First Step", "content": "Content of the first chapter."},
            {"chapter_number": 2, "title": "The Second Step", "content": "Content of the second chapter."},
        ]

        mock_context_agent_instance.run.assert_called_once_with({
            "chapters": expected_chapters_data,
            "world_setting": mock_ws_model.content,
            "character_profiles": [mock_char_model.content],
            "key_events": [], # Passed as empty by the service
            "character_states": {}, # Passed as empty by the service
            "mode": "layered"
        })

        # Verify the output formatting from _get_previous_summary itself
        self.assertIn("### 长期故事脉络回顾 (Long-Term Context):", formatted_summary)
        self.assertIn("Service: Mocked Long Term Summary.", formatted_summary)
        self.assertIn("### 中期剧情发展 (Medium-Term Context - Last 5-10 Chapters):", formatted_summary)
        self.assertIn("Service: Mocked Medium Term Summary.", formatted_summary)
        self.assertIn("### 最新即时情境 (Recent Context - Last 1-3 Chapters):", formatted_summary)
        self.assertIn("Service: Mocked Recent Summary.", formatted_summary)
        self.assertIn("### 综合前情提要 (Overall Summary for this Chapter):", formatted_summary)
        self.assertIn("Service: Mocked Overall Comprehensive Summary.", formatted_summary)

    async def test_get_previous_summary_for_first_chapter(self):
        summary = await self.service._get_previous_summary("test_project_id", 1)
        self.assertEqual(summary, "这是故事的第一章，没有前情提要。")

    async def test_get_previous_summary_no_prior_chapters_data(self):
        self.service.chapter_repo.get_by_project_id = MagicMock(return_value=[]) # No chapters returned
        summary = await self.service._get_previous_summary("test_project_id", 2) # For chapter 2, but no data for ch1
        self.assertEqual(summary, "这是故事的第一章（或前面的章节数据丢失），没有足够的前情提要。")


if __name__ == '__main__':
    unittest.main()
