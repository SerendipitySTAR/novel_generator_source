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

            # Check that revision_guidance is empty when no feedback is provided
            self.assertEqual(prompt_data_arg["revision_guidance"], "")


    async def test_generate_chapter_prompt_with_retry_feedback(self):
        # Mock LLM response
        self.mock_llm.generate_text.return_value = LLMResponse(text="Generated chapter content after feedback.")

        # Mock _generate_enhanced_summary
        self.agent._generate_enhanced_summary = AsyncMock(return_value="FORMATTED SUMMARY")

        mock_retry_feedback = {
            "audit_report": {
                "具体问题点": ["Issue 1 from audit.", "Issue 2 from audit."],
                "改进建议": ["Suggestion A from audit.", "Suggestion B from audit."]
            },
            "improvement_suggestions": ["General suggestion C."], # Test merging if both exist
            "negative_aspects": ["A general negative point."]
        }

        formatted_feedback_expected_str = self.agent._format_retry_feedback(mock_retry_feedback)

        input_data_with_feedback = {
            "chapter_outline": {"number": 2, "title": "The Second Try", "word_count": 150},
            "world_setting": {}, "character_profiles": [], "writing_style": "Concise",
            "retry_count": 1, # Important for {retry_guidance}
            "retry_feedback": mock_retry_feedback
        }

        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Prompt With Feedback"

            # Patch _format_retry_feedback to check it's called and to control its output if needed,
            # or just use the real method and check against its expected output.
            # For this test, let's use the real method's output.

            await self.agent._generate_chapter(input_data_with_feedback)

            args, _ = mock_generate_prompt.call_args
            prompt_template_arg = args[0]
            prompt_data_arg = args[1]

            self.assertIn("{revision_guidance}", prompt_template_arg)
            self.assertIn("## 针对上一版内容的修改建议 (Suggestions for Revising the Previous Version):", prompt_data_arg["revision_guidance"])
            self.assertIn("Issue 1 from audit.", prompt_data_arg["revision_guidance"])
            self.assertIn("Suggestion A from audit.", prompt_data_arg["revision_guidance"])
            self.assertIn("General suggestion C.", prompt_data_arg["revision_guidance"])
            self.assertIn("A general negative point.", prompt_data_arg["revision_guidance"])

            self.assertEqual(prompt_data_arg["revision_guidance"], f"## 针对上一版内容的修改建议 (Suggestions for Revising the Previous Version):\n{formatted_feedback_expected_str}")

            # Ensure generic retry_guidance is also present
            self.assertIn("重试指导（第2次生成）", prompt_data_arg["retry_guidance"])


    def test_format_retry_feedback_quality_guardian_style(self):
        feedback = {
            "evaluation_reasons": {"情节连贯性": "有点跳跃 (A bit jumpy)"},
            "improvement_suggestions": ["增加过渡场景 (Add transition scene)"]
        }
        expected = "根据上一版的评估，请注意以下几点：\n- 情节连贯性相关问题: 有点跳跃 (A bit jumpy)\n\n改进建议如下：\n  - 增加过渡场景 (Add transition scene)"
        self.assertEqual(self.agent._format_retry_feedback(feedback), expected)

    def test_format_retry_feedback_content_integrity_style(self):
        feedback = {
            "audit_report": {
                "具体问题点": ["人物动机不明确 (Character motivation unclear)"],
                "改进建议": ["在前文铺垫一下心理活动 (Foreshadow psychological activity earlier)"]
            }
        }
        expected = "根据上一版的评估，请注意以下几点：\n\n上一版内容存在以下具体问题点：\n  - 问题1: 人物动机不明确 (Character motivation unclear)\n\n针对这些问题的改进建议：\n  - 建议1: 在前文铺垫一下心理活动 (Foreshadow psychological activity earlier)"
        # The initial "根据上一版的评估..." comes because audit_report is not the first check in _format_retry_feedback,
        # and the list `parts` is initialized with it if evaluation_reasons or improvement_suggestions are checked first.
        # This is acceptable, or the _format_retry_feedback can be made more mutually exclusive.
        # For now, let's assume the current logic of _format_retry_feedback which might prepend the generic line.
        # Actually, the current logic will produce the "根据上一版的评估..." only if "evaluation_reasons" or "improvement_suggestions" is present.
        # Let's adjust the expected for current logic:
        expected_direct = "上一版内容存在以下具体问题点：\n  - 问题1: 人物动机不明确 (Character motivation unclear)\n\n针对这些问题的改进建议：\n  - 建议1: 在前文铺垫一下心理活动 (Foreshadow psychological activity earlier)"
        # Re-evaluating _format_retry_feedback, the first `if` is `if "evaluation_reasons" in feedback or "improvement_suggestions" in feedback:`.
        # If these are not present, the "根据上一版的评估..." line is NOT added. This is correct.
        self.assertEqual(self.agent._format_retry_feedback(feedback), expected_direct)


    def test_format_retry_feedback_direct_negatives_and_suggestions(self):
        feedback = {
            "negative_aspects": ["节奏太慢 (Pacing too slow)"],
            "improvement_suggestions": ["删除不必要的描写 (Remove unnecessary descriptions)"]
        }
        # Expected will include the intro line for improvement_suggestions.
        expected = "根据上一版的评估，请注意以下几点：\n\n改进建议如下：\n  - 删除不必要的描写 (Remove unnecessary descriptions)\n\n先前版本的主要问题：\n  - 节奏太慢 (Pacing too slow)"
        self.assertEqual(self.agent._format_retry_feedback(feedback), expected)

        feedback_only_neg = {"negative_aspects": ["节奏太慢 (Pacing too slow)"]}
        expected_only_neg = "先前版本的主要问题：\n  - 节奏太慢 (Pacing too slow)"
        self.assertEqual(self.agent._format_retry_feedback(feedback_only_neg), expected_only_neg)


    def test_format_retry_feedback_empty_or_partial(self):
        self.assertEqual(self.agent._format_retry_feedback({}), "请根据之前的反馈进行修改和提升。")
        self.assertEqual(self.agent._format_retry_feedback({"improvement_suggestions": []}), "请根据之前的反馈进行修改和提升。")
        feedback_empty_reason = {"evaluation_reasons": {"some_key": ""}}
        self.assertEqual(self.agent._format_retry_feedback(feedback_empty_reason), "请根据之前的反馈进行修改和提升。")
        feedback_empty_audit = {"audit_report": {"具体问题点": [], "改进建议": []}}
        self.assertEqual(self.agent._format_retry_feedback(feedback_empty_audit), "请根据之前的反馈进行修改和提升。")

    def test_format_retry_feedback_no_issues_found_style(self):
        feedback = {"evaluation_reasons": {}, "improvement_suggestions": []} # Empty but keys exist
        self.assertEqual(self.agent._format_retry_feedback(feedback), "请根据之前的反馈进行修改和提升。")


if __name__ == '__main__':
    unittest.main()
