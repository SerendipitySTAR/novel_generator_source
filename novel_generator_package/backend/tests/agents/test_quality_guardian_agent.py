import pytest
import unittest
from unittest.mock import AsyncMock, patch
import json

from app.agents.quality_guardian import QualityGuardianAgent
from app.core.llm import LLMResponse

class TestQualityGuardianAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = QualityGuardianAgent(llm=self.mock_llm, project_id="test_project")

    async def test_evaluate_chapter_content_prompt_includes_new_considerations(self):
        # Mock LLM response
        mock_response_json = {
            "dimension_scores": {
                "情节连贯性": 18, "人物一致性": 17, "文笔质量": 18,
                "节奏把控": 17, "情感渲染": 18
            },
            "total_score": 88,
            "evaluation_reasons": {"综合": "Good chapter."},
            "improvement_suggestions": ["None needed."]
        }
        self.mock_llm.generate_text.return_value = LLMResponse(text=json.dumps(mock_response_json))

        input_data_chapter = {
            "content_type": "chapter",
            "content": "This is a test chapter about brave heroes.",
            "context": { # Provide some context for completeness
                "previous_chapters": [{"title": "Prev Ch", "content": "Once upon a time"}],
                "character_profiles": [{"人物设定": [{"基本信息": {"姓名": "Hero"}}]}],
                "world_setting": {"基本设定": {"世界名称": "Test World"}}
            }
        }

        # Spy on the _generate_prompt method
        # Since the routing to _evaluate_chapter_content is internal,
        # we'll patch _generate_prompt for that specific method call if possible,
        # or check the prompt passed to the LLM by the top-level run method.
        # For simplicity, we trust run() calls the correct internal eval method and check its prompt.

        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Quality Guardian Chapter Prompt"

            await self.agent.run(input_data_chapter)

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Quality Guardian Chapter Prompt",
                temperature=unittest.mock.ANY,
                max_tokens=unittest.mock.ANY,
                top_p=unittest.mock.ANY
            )

            called_prompt_template_str = mock_generate_prompt.call_args[0][0]

            self.assertIn("在进行上述评估时，请特别针对章节内容，额外深入思考以下几个方面", called_prompt_template_str)
            self.assertIn("创新性 (Innovativeness)", called_prompt_template_str)
            self.assertIn("情感深度 (Emotional Depth)", called_prompt_template_str)
            self.assertIn("角色弧光进展 (Character Arc Progression)", called_prompt_template_str)
            # Verify instruction for actionable feedback
            self.assertIn("请确保指出的不足之处和改进建议是具体且可操作的，能够清晰地指导内容的修订。", called_prompt_template_str)


    async def _test_prompt_for_actionable_feedback(self, content_type: str, content_payload: Any, mock_response_json: Dict, expected_phrase: str):
        self.mock_llm.generate_text.return_value = LLMResponse(text=json.dumps(mock_response_json))
        input_data = {"content_type": content_type, "content": content_payload}

        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = f"Final Prompt for {content_type}"
            await self.agent.run(input_data)
            called_prompt_template_str = mock_generate_prompt.call_args[0][0]
            self.assertIn(expected_phrase, called_prompt_template_str)
            # Ensure chapter-specific considerations are NOT in non-chapter prompts
            if content_type != "chapter":
                 self.assertNotIn("在进行上述评估时，请特别针对章节内容，额外深入思考以下几个方面", called_prompt_template_str)
                 self.assertNotIn("角色弧光进展 (Character Arc Progression)", called_prompt_template_str)


    async def test_evaluate_narrative_concept_prompt_actionable(self):
        await self._test_prompt_for_actionable_feedback(
            content_type="concept",
            content_payload="Test concept.",
            mock_response_json={"total_score": 0, "dimension_scores": {}, "evaluation_reasons": {}, "improvement_suggestions": []},
            expected_phrase="请确保这些建议具体且可操作，能够清晰地指导内容的修订。"
        )

    async def test_evaluate_world_setting_prompt_actionable(self):
        await self._test_prompt_for_actionable_feedback(
            content_type="world_setting",
            content_payload={"description": "Test world."},
            mock_response_json={"total_score": 0, "dimension_scores": {}, "evaluation_reasons": {}, "improvement_suggestions": []},
            expected_phrase="请确保这些建议具体且可操作。"
        )

    async def test_evaluate_plot_outline_prompt_actionable(self):
        await self._test_prompt_for_actionable_feedback(
            content_type="plot_outline",
            content_payload={"structure": "Test plot."},
            mock_response_json={"total_score": 0, "dimension_scores": {}, "evaluation_reasons": {}, "improvement_suggestions": []},
            expected_phrase="请确保这些建议具体且可操作。"
        )

    async def test_evaluate_character_profiles_prompt_actionable(self):
        await self._test_prompt_for_actionable_feedback(
            content_type="character_profiles",
            content_payload=[{"name": "Test char"}],
            mock_response_json={"total_score": 0, "dimension_scores": {}, "evaluation_reasons": {}, "improvement_suggestions": []},
            expected_phrase="请确保这些建议具体且可操作。"
        )

    # test_evaluate_other_content_types_prompt_excludes_chapter_specifics can be removed or refactored
    # as the new helper _test_prompt_for_actionable_feedback also checks for exclusion.
    # For now, let's keep it to ensure its original purpose (checking exclusion) is explicitly clear.
    async def test_evaluate_concept_prompt_excludes_chapter_specifics(self): # Renamed for clarity
        mock_response_json_concept = {
            "dimension_scores": {"情节新颖度": 20, "冲突潜力": 20, "角色魅力潜力": 20, "主题深度潜力": 20},
            "total_score": 80,
            "evaluation_reasons": {"综合": "Good concept."},
            "improvement_suggestions": ["Expand on X."]
        }
        self.mock_llm.generate_text.return_value = LLMResponse(text=json.dumps(mock_response_json_concept))

        input_data_concept = {
            "content_type": "concept",
            "content": "A concept about a space wizard."
        }

        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Quality Guardian Concept Prompt"

            await self.agent.run(input_data_concept)

            called_prompt_template_str = mock_generate_prompt.call_args[0][0]

            self.assertNotIn("在进行上述评估时，请特别针对章节内容，额外深入思考以下几个方面", called_prompt_template_str)
            self.assertNotIn("角色弧光进展 (Character Arc Progression)", called_prompt_template_str)


if __name__ == '__main__':
    unittest.main()
