import pytest
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.context_synthesizer import ContextSynthesizerAgent
from app.core.llm import LLMResponse

# Sample data to be used in tests
mock_chapters = [
    {"chapter_number": 1, "title": "Chapter 1", "content": "Content of chapter 1."},
    {"chapter_number": 2, "title": "Chapter 2", "content": "Content of chapter 2."},
    {"chapter_number": 3, "title": "Chapter 3", "content": "Content of chapter 3."},
    {"chapter_number": 4, "title": "Chapter 4", "content": "Content of chapter 4."},
    {"chapter_number": 5, "title": "Chapter 5", "content": "Content of chapter 5."},
    {"chapter_number": 6, "title": "Chapter 6", "content": "Content of chapter 6."},
]
mock_world_setting = {"description": "A fantasy world."}
mock_character_profiles = [{"name": "Alice", "description": "A brave adventurer."}]
mock_key_events = [{"event": "The Great Battle", "chapter": 1}]
mock_character_states = {"Alice": {"location": "Forest", "mood": "determined"}}

class TestContextSynthesizerAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = ContextSynthesizerAgent(llm=self.mock_llm)

    async def test_generate_layered_context_calls_helpers_and_assembles(self):
        # Mock the helper methods' LLM calls and their direct outputs
        self.mock_llm.generate_text.side_effect = [
            LLMResponse(text="Mocked Long Term Summary"),    # For _build_long_term_context
            LLMResponse(text="Mocked Medium Term Summary"),   # For _build_medium_context
            LLMResponse(text="Mocked Recent Summary"),       # For _build_immediate_context (recent)
            LLMResponse(text="Mocked Comprehensive Summary") # For _build_comprehensive_summary
        ]

        # Patch the helper methods themselves to check they are called
        with patch.object(self.agent, '_build_long_term_context', new_callable=AsyncMock, return_value="Patched Long Term Summary") as mock_long, \
             patch.object(self.agent, '_build_medium_context', new_callable=AsyncMock, return_value="Patched Medium Term Summary") as mock_medium, \
             patch.object(self.agent, '_build_immediate_context', new_callable=AsyncMock, return_value="Patched Recent Summary") as mock_recent, \
             patch.object(self.agent, '_build_comprehensive_summary', new_callable=AsyncMock, return_value="Patched Comprehensive Summary") as mock_comprehensive:

            result = await self.agent._generate_layered_context(
                chapters=mock_chapters,
                world_setting=mock_world_setting,
                character_profiles=mock_character_profiles,
                key_events=mock_key_events,
                character_states=mock_character_states
            )

            mock_long.assert_called_once_with(mock_chapters, mock_key_events, mock_character_states, mock_world_setting, mock_character_profiles)
            mock_medium.assert_called_once_with(mock_chapters, mock_key_events)
            mock_recent.assert_called_once_with(mock_chapters)
            mock_comprehensive.assert_called_once_with("Patched Long Term Summary", "Patched Medium Term Summary", "Patched Recent Summary")

            self.assertEqual(result["long_term_summary"], "Patched Long Term Summary")
            self.assertEqual(result["medium_summary"], "Patched Medium Term Summary")
            self.assertEqual(result["recent_summary"], "Patched Recent Summary")
            self.assertEqual(result["summary"], "Patched Comprehensive Summary")

            # Ensure that the direct LLM calls were not made by _generate_layered_context itself
            # but rather by the (now patched) helper methods.
            # The number of calls to generate_text should correspond to the number of times the original helpers would call it.
            # Since we patched the helpers directly, generate_text on self.mock_llm itself shouldn't be called by _generate_layered_context
            # but if we were testing the helpers, they would call it.
            # For this specific test, if helpers are patched, self.mock_llm.generate_text might not be called at all if the patched versions don't call it.
            # Let's refine this: we test helper calls, and then we test helpers individually for their prompt generation.

    async def test_build_long_term_context_prompt(self):
        self.mock_llm.generate_text.return_value = LLMResponse(text="Long term output")

        # Spy on _generate_prompt
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_gen_prompt:
            mock_gen_prompt.return_value = "Final Long Term Prompt" # Dummy prompt string
            await self.agent._build_long_term_context(
                chapters=mock_chapters,
                key_events=mock_key_events,
                character_states=mock_character_states,
                world_setting=mock_world_setting,
                character_profiles=mock_character_profiles
            )

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Long Term Prompt",
                temperature=0.5,
                max_tokens=800,
                top_p=unittest.mock.ANY # Assuming top_p comes from settings
            )

            # Check what was passed to _generate_prompt
            args, _ = mock_gen_prompt.call_args
            prompt_template_arg = args[0] # The template string
            prompt_data_arg = args[1] # The dictionary of data

            self.assertIn("至今的全部章节摘要", prompt_template_arg)
            self.assertIn("chapters_summary_text", prompt_data_arg)
            self.assertTrue(len(prompt_data_arg["chapters_summary_text"]) > 0)
            # Check if chapter summarization happened (e.g. content is shortened)
            self.assertTrue(mock_chapters[0]['content'][:100] in prompt_data_arg["chapters_summary_text"])


    async def test_build_medium_context_prompt_chapter_slicing(self):
        self.mock_llm.generate_text.return_value = LLMResponse(text="Medium term output")

        # Test with more than 10 chapters to verify slicing
        many_chapters = [{"chapter_number": i, "title": f"Ch {i}", "content": f"Content {i}"} for i in range(1, 15)] # 14 chapters

        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_gen_prompt:
            mock_gen_prompt.return_value = "Final Medium Prompt"
            await self.agent._build_medium_context(chapters=many_chapters, key_events=mock_key_events)

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Medium Prompt", temperature=0.4, max_tokens=600, top_p=unittest.mock.ANY
            )
            args, _ = mock_gen_prompt.call_args
            prompt_data_arg = args[1]
            # Should contain summaries of last 10 chapters (Ch 5 to Ch 14)
            self.assertIn("Ch 5", prompt_data_arg["medium_term_chapters_text"])
            self.assertIn("Ch 14", prompt_data_arg["medium_term_chapters_text"])
            self.assertNotIn("Ch 4", prompt_data_arg["medium_term_chapters_text"])
            self.assertTrue(prompt_data_arg["medium_term_chapters_text"].count("Ch ") == 10)

        # Test with 5 chapters (should take all 5)
        self.mock_llm.generate_text.reset_mock() # Reset call count for next assertion
        mock_gen_prompt.reset_mock()
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_gen_prompt_short: # new mock for clarity
            mock_gen_prompt_short.return_value = "Final Medium Prompt Short"
            await self.agent._build_medium_context(chapters=mock_chapters[:5], key_events=mock_key_events) # First 5 chapters

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Medium Prompt Short", temperature=0.4, max_tokens=600, top_p=unittest.mock.ANY
            )
            args_short, _ = mock_gen_prompt_short.call_args
            prompt_data_short_arg = args_short[1]
            self.assertTrue(prompt_data_short_arg["medium_term_chapters_text"].count("第") == 5 or prompt_data_short_arg["medium_term_chapters_text"].count("Ch") == 5)


    async def test_build_immediate_context_prompt_chapter_slicing(self):
        self.mock_llm.generate_text.return_value = LLMResponse(text="Immediate output")

        # Test with more than 3 chapters
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_gen_prompt:
            mock_gen_prompt.return_value = "Final Immediate Prompt"
            await self.agent._build_immediate_context(chapters=mock_chapters) # mock_chapters has 6 chapters

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Immediate Prompt", temperature=0.3, max_tokens=300, top_p=unittest.mock.ANY
            )
            args, _ = mock_gen_prompt.call_args
            prompt_data_arg = args[1]
            # Should contain summaries of last 3 chapters (4, 5, 6)
            self.assertIn(mock_chapters[3]["title"], prompt_data_arg["recent_chapters_text"]) # Chapter 4
            self.assertIn(mock_chapters[5]["title"], prompt_data_arg["recent_chapters_text"]) # Chapter 6
            self.assertNotIn(mock_chapters[2]["title"], prompt_data_arg["recent_chapters_text"]) # Chapter 3
            self.assertTrue(prompt_data_arg["recent_chapters_text"].count("###") == 3) # Markdown heading for each chapter

        # Test with 1 chapter
        self.mock_llm.generate_text.reset_mock()
        mock_gen_prompt.reset_mock()
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_gen_prompt_one:
            mock_gen_prompt_one.return_value = "Final Immediate Prompt One"
            await self.agent._build_immediate_context(chapters=mock_chapters[:1]) # Only first chapter

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Immediate Prompt One", temperature=0.3, max_tokens=300, top_p=unittest.mock.ANY
            )
            args_one, _ = mock_gen_prompt_one.call_args
            prompt_data_one_arg = args_one[1]
            self.assertTrue(prompt_data_one_arg["recent_chapters_text"].count("###") == 1)


    async def test_build_comprehensive_summary_prompt(self):
        self.mock_llm.generate_text.return_value = LLMResponse(text="Comprehensive output")

        long_context = "Test long context."
        medium_context = "Test medium context."
        recent_context = "Test recent context."

        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_gen_prompt:
            mock_gen_prompt.return_value = "Final Comprehensive Prompt"
            await self.agent._build_comprehensive_summary(long_context, medium_context, recent_context)

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Comprehensive Prompt", temperature=0.4, max_tokens=700, top_p=unittest.mock.ANY
            )
            args, _ = mock_gen_prompt.call_args
            prompt_data_arg = args[1]
            self.assertEqual(prompt_data_arg["long_term_context"], long_context)
            self.assertEqual(prompt_data_arg["medium_context"], medium_context)
            self.assertEqual(prompt_data_arg["recent_context"], recent_context)

if __name__ == '__main__':
    unittest.main()
