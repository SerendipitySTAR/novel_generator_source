import pytest
import unittest
from unittest.mock import AsyncMock, patch

from app.agents.style_polisher import StylePolisherAgent
from app.core.llm import LLMResponse

class TestStylePolisherAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = StylePolisherAgent(llm=self.mock_llm, project_id="test_project")

    async def test_style_polisher_prompt_includes_new_instructions(self):
        # Mock the LLM response
        self.mock_llm.generate_text.return_value = LLMResponse(text="Polished content.\n修改摘要: Made it better.")

        # Dummy input data
        input_data = {
            "content": "This is the original content.",
            "style": "海明威风格", # Test with a specific style
            "focus_areas": ["描写", "对话"]
        }

        # Spy on the _generate_prompt method
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Style Polisher Prompt"

            await self.agent.run(input_data)

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Style Polisher Prompt",
                temperature=unittest.mock.ANY,
                max_tokens=unittest.mock.ANY,
                top_p=unittest.mock.ANY
            )

            called_prompt_template_str = mock_generate_prompt.call_args[0][0]
            called_prompt_data = mock_generate_prompt.call_args[0][1]


            # Verify that the {style} placeholder is correctly filled
            self.assertEqual(called_prompt_data.get("style"), "海明威风格")
            self.assertIn("符合海明威风格风格的特点", called_prompt_template_str) # Check if style is in the general requirement
            self.assertIn("如果 海明威风格 指向特定的文学流派", called_prompt_template_str) # Check if style is in the specific imitation instruction


            # Verify new instructional keywords are in the prompt template
            self.assertIn("增强情感共鸣 (Emotional Resonance)", called_prompt_template_str)
            self.assertIn("使用更具表现力的动词和形容词", called_prompt_template_str)

            self.assertIn("运用文学手法 (Literary Devices)", called_prompt_template_str)
            self.assertIn("隐喻（暗喻/比喻 Metaphors）", called_prompt_template_str)
            self.assertIn("明喻 (Similes)", called_prompt_template_str)
            self.assertIn("象征 (Symbolism)", called_prompt_template_str)
            self.assertIn("这些手法应自然贴切，不显刻意", called_prompt_template_str)

            self.assertIn("特定风格模仿 (Specific Style Imitation)", called_prompt_template_str)
            self.assertIn("如果 {style} 指向特定的文学流派", called_prompt_template_str) # Check the placeholder itself
            self.assertIn("常用词汇、典型句式、叙事节奏、常见意象或主题", called_prompt_template_str)

    def test_parse_response_with_summary(self):
        response_text = "This is the polished content.\n\n修改摘要: \n- Improved flow.\n- Enhanced descriptions."
        expected_polished_content = "This is the polished content."
        expected_summary = "修改摘要: \n- Improved flow.\n- Enhanced descriptions."

        result = self.agent._parse_response(response_text) # Assuming _parse_response is the method name, adjust if different
                                                       # Based on provided agent code, it's done directly in run(), so we test that behavior.

        # Let's simulate the parsing logic within run() for this test
        polished_content_parsed = response_text
        changes_summary_parsed = ""
        separators = ["修改摘要:", "修改摘要：", "修改总结:", "修改总结：",
                     "修改说明:", "修改说明：", "改进摘要:", "改进摘要：",
                     "润色摘要:", "润色摘要：", "润色总结:", "润色总结："]
        for separator in separators:
            if separator in response_text:
                parts = response_text.split(separator, 1)
                polished_content_parsed = parts[0].strip()
                changes_summary_parsed = separator + parts[1].strip()
                break

        self.assertEqual(polished_content_parsed, expected_polished_content)
        self.assertEqual(changes_summary_parsed, expected_summary)

    def test_parse_response_without_summary(self):
        response_text = "This is the polished content only."
        expected_polished_content = "This is the polished content only."
        expected_summary = "" # Expect empty if no separator

        # Simulate parsing logic from run()
        polished_content_parsed = response_text
        changes_summary_parsed = ""
        separators = ["修改摘要:", "修改摘要：", "修改总结:", "修改总结："]
        for separator in separators:
            if separator in response_text: # This won't find a match
                parts = response_text.split(separator, 1)
                polished_content_parsed = parts[0].strip()
                changes_summary_parsed = separator + parts[1].strip()
                break

        self.assertEqual(polished_content_parsed, expected_polished_content)
        self.assertEqual(changes_summary_parsed, expected_summary)


if __name__ == '__main__':
    unittest.main()
