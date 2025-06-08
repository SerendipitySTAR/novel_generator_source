import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.chapter_chronicler import ChapterChroniclerAgent
from app.core.llm import LLMResponse

mock_llm_instance = AsyncMock()

class TestChapterChroniclerAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = ChapterChroniclerAgent(llm=self.mock_llm, project_id="test_project")

    @patch('app.agents.chapter_chronicler.ContextSynthesizerAgent', autospec=True)
    async def test_generate_enhanced_summary_formatting(self, MockContextSynthesizerAgent):
        # Mock the ContextSynthesizerAgent's run method
        mock_context_agent_instance = MockContextSynthesizerAgent.return_value
        mock_context_agent_instance.run = AsyncMock(return_value={
            "long_term_summary": "Mocked Long Term Summary.",
            "medium_summary": "Mocked Medium Term Summary.",
            "recent_summary": "Mocked Recent Summary.",
            "summary": "Mocked Overall Comprehensive Summary."
        })

        # Dummy inputs for _generate_enhanced_summary
        previous_chapters = [{"chapter_number": 1, "content": "Previous chapter content."}]
        world_setting = {"description": "A test world."}
        character_profiles = [{"name": "Test Character"}]
        basic_summary = "This is a basic summary." # This should be largely overridden by the comprehensive one

        formatted_summary = await self.agent._generate_enhanced_summary(
            previous_chapters, world_setting, character_profiles, basic_summary
        )

        # Verify ContextSynthesizerAgent was called correctly
        MockContextSynthesizerAgent.assert_called_once_with(llm=self.mock_llm) # Check if agent was initialized with the LLM
        mock_context_agent_instance.run.assert_called_once_with({
            "chapters": previous_chapters,
            "world_setting": world_setting,
            "character_profiles": character_profiles,
            "mode": "layered"
            # key_events and character_states are not passed by ChapterChroniclerAgent's _generate_enhanced_summary
            # so they should not be in this call. ContextSynthesizerAgent handles their absence.
        })

        # Verify the output formatting
        self.assertIn("### 长期故事脉络回顾 (Long-Term Context):", formatted_summary)
        self.assertIn("Mocked Long Term Summary.", formatted_summary)
        self.assertIn("### 中期剧情发展 (Medium-Term Context - Last 5-10 Chapters):", formatted_summary)
        self.assertIn("Mocked Medium Term Summary.", formatted_summary)
        self.assertIn("### 最新即时情境 (Recent Context - Last 1-3 Chapters):", formatted_summary)
        self.assertIn("Mocked Recent Summary.", formatted_summary)
        self.assertIn("### 综合前情提要 (Overall Summary for this Chapter):", formatted_summary)
        self.assertIn("Mocked Overall Comprehensive Summary.", formatted_summary)

    async def test_generate_chapter_prompt_incorporates_new_params_and_summary(self):
        # Mock LLM response
        self.mock_llm.generate_text.return_value = LLMResponse(text="Generated chapter content.")

        # Mock _generate_enhanced_summary to return a known string
        mock_enhanced_summary_str = "FORMATTED ENHANCED SUMMARY STRING"
        self.agent._generate_enhanced_summary = AsyncMock(return_value=mock_enhanced_summary_str)

        # Spy on _generate_prompt
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Chapter Prompt" # Dummy prompt

            # Inputs for _generate_chapter
            input_data = {
                "chapter_outline": {"number": 1, "title": "The Beginning", "scenes": "Scene 1", "events": "Event 1", "word_count": 100},
                "world_setting": {"description": "A test world"},
                "character_profiles": [{"characters": [{"name": "Hero"}]}],
                "previous_summary": "Old summary (should be replaced by enhanced)",
                "writing_style": "Epic",
                # New parameters
                "novel_progress": 0.1, # Early novel
                "tension_level": "rising",
                "chapter_type": "introduction",
                "long_term_goals": ["Introduce the main conflict", "Establish character A's motivation"],
                "previous_chapters": [] # Needed for _generate_enhanced_summary if not mocked at a higher level
            }

            await self.agent._generate_chapter(input_data)

            # Assert _generate_enhanced_summary was called (it is, as it's a direct call)
            self.agent._generate_enhanced_summary.assert_called_once()

            # Assert LLM was called with the dummy prompt from the mocked _generate_prompt
            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Chapter Prompt",
                temperature=0.7,
                max_tokens=unittest.mock.ANY, # Assuming this comes from settings
                top_p=0.9
            )

            # Check the arguments passed to the (mocked) _generate_prompt
            args, _ = mock_generate_prompt.call_args
            prompt_template_arg = args[0] # The template string itself
            prompt_data_arg = args[1] # The dictionary of data for the template

            # Verify enhanced summary is in the prompt data
            self.assertEqual(prompt_data_arg["enhanced_summary"], mock_enhanced_summary_str)

            # Verify new parameters are in the prompt data
            self.assertEqual(prompt_data_arg["novel_progress"], input_data["novel_progress"])
            self.assertEqual(prompt_data_arg["tension_level"], input_data["tension_level"])
            self.assertEqual(prompt_data_arg["chapter_type"], input_data["chapter_type"])
            self.assertEqual(prompt_data_arg["long_term_goals"], input_data["long_term_goals"])

            # Verify new parameters are mentioned in the prompt template structure
            self.assertIn("章节叙事策略", prompt_template_arg)
            self.assertIn("Novel Progress", prompt_template_arg)
            self.assertIn("Chapter Type", prompt_template_arg)
            self.assertIn("Target Tension Level", prompt_template_arg)
            self.assertIn("Relevant Long-term Goals/Threads", prompt_template_arg)
            self.assertIn("{novel_progress}", prompt_template_arg)
            self.assertIn("{tension_level}", prompt_template_arg)
            self.assertIn("{chapter_type}", prompt_template_arg)
            self.assertIn("{long_term_goals}", prompt_template_arg)

            # Assertions for refined chapter rhythm control (new in this subtask)
            self.assertIn("具体示例", prompt_template_arg) # "Specific Examples"
            self.assertIn("若 `chapter_type` 是 '铺垫型 (setup)' 且 `tension_level` 是 '低 (low)'", prompt_template_arg)
            self.assertIn("若 `chapter_type` 是 '冲突型 (conflict)' 或 '高潮型 (climax)'", prompt_template_arg)
            self.assertIn("请将这些建议视为参考，并根据具体章节大纲和创意灵活运用", prompt_template_arg)

            # Assertions for immersive scene setting (new in this subtask)
            self.assertIn("沉浸式场景构建 (Immersive Scene Setting)", prompt_template_arg)
            self.assertIn("调动多重感官", prompt_template_arg) # "Engage multiple senses"
            self.assertIn("视觉 (Visuals)", prompt_template_arg)
            self.assertIn("听觉 (Sounds)", prompt_template_arg)
            self.assertIn("嗅觉 (Smells)", prompt_template_arg)
            self.assertIn("触觉 (Tactile)", prompt_template_arg)
            self.assertIn("味觉 (Taste)", prompt_template_arg)
            self.assertIn("自然融入", prompt_template_arg) # "Natural Integration"


if __name__ == '__main__':
    unittest.main()
