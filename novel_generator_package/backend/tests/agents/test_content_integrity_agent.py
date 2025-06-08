import pytest
import unittest
from unittest.mock import AsyncMock, patch
import json

from app.agents.content_integrity import ContentIntegrityAgent
from app.core.llm import LLMResponse

class TestContentIntegrityAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = ContentIntegrityAgent(llm=self.mock_llm, project_id="test_project")

    async def test_full_content_audit_prompt_includes_new_dimensions(self):
        self.mock_llm.generate_text.return_value = LLMResponse(text='{"dimension_scores": {}, "total_score": 0, "audit_report": {}}')

        input_data = {
            "chapter_content": "Test chapter content.",
            "chapter_outline": {"title": "Test Outline"},
            "character_profiles": [{"人物设定": [{"基本信息": {"姓名": "Test Character"}}]}],
            "kb_snapshot": {},
            "writing_style": "Test Style",
            "previous_chapters": [],
            "world_setting": {}
        }

        # Spy on the _generate_prompt method
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Content Integrity Prompt"

            await self.agent._full_content_audit(**input_data)

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Content Integrity Prompt",
                temperature=unittest.mock.ANY,
                max_tokens=unittest.mock.ANY,
                top_p=unittest.mock.ANY
            )

            called_prompt_template_str = mock_generate_prompt.call_args[0][0]

            # Verify new dimensions and their descriptions are in the prompt
            self.assertIn("创新性 (Innovativeness)** (10分): 情节、角色或设定是否有新颖之处？是否避免了常见的陈词滥调？", called_prompt_template_str)
            self.assertIn("情感深度 (Emotional Depth)** (10分): 角色情感是否真实可信？能否引发读者的情感投入？场景氛围是否营造到位？", called_prompt_template_str)
            self.assertIn("角色弧光完整性 (Character Arc Completeness)** (10分): 主要角色在本章中是否有所发展或变化（即使是微小的），是否为其整体弧光做出贡献或铺垫？", called_prompt_template_str)

            # Verify score changes for existing dimensions (example)
            self.assertIn("逻辑连贯性 (Logical Coherence)** (10分)", called_prompt_template_str)
            self.assertIn("情节吸引力 (Plot Engagement)** (10分)", called_prompt_template_str)
            self.assertNotIn("情节一致性（20分）", called_prompt_template_str) # Old version
            self.assertNotIn("人物一致性（20分）", called_prompt_template_str) # Old version

            # Verify example JSON in prompt includes new keys
            self.assertIn('"创新性": 分数', called_prompt_template_str)
            self.assertIn('"情感深度": 分数', called_prompt_template_str)
            self.assertIn('"角色弧光完整性": 分数', called_prompt_template_str)
            self.assertIn('"逻辑连贯性": 分数', called_prompt_template_str) # New name for old criteria

    async def test_full_content_audit_parsing_with_new_dimensions(self):
        mock_response_json = {
            "dimension_scores": {
                "逻辑连贯性": 9,
                "情节吸引力": 8,
                "人物一致性": 7,
                "世界观契合度": 9,
                "写作风格与流畅度": 8,
                "对话自然度与功能性": 7,
                "整体可读性": 8,
                "创新性": 9,
                "情感深度": 8,
                "角色弧光完整性": 7
            },
            "total_score": 80, # Sum of above example scores is 80
            "audit_report": {
                "总体评价": "Good chapter overall.",
                "具体问题点": ["Minor pacing issue."],
                "改进建议": ["Tighten pacing in scene 2."]
            }
        }
        self.mock_llm.generate_text.return_value = LLMResponse(text=json.dumps(mock_response_json))

        input_data = {
            "chapter_content": "Test chapter content.",
            "chapter_outline": {}, "character_profiles": [], "kb_snapshot": {},
            "writing_style": "Test Style", "previous_chapters": [], "world_setting": {}
        }

        result = await self.agent._full_content_audit(**input_data)

        self.assertEqual(result["total_score"], 80)
        self.assertIn("创新性", result["dimension_scores"])
        self.assertEqual(result["dimension_scores"]["创新性"], 9)
        self.assertIn("情感深度", result["dimension_scores"])
        self.assertEqual(result["dimension_scores"]["情感深度"], 8)
        self.assertIn("角色弧光完整性", result["dimension_scores"])
        self.assertEqual(result["dimension_scores"]["角色弧光完整性"], 7)
        self.assertEqual(result["audit_report"]["总体评价"], "Good chapter overall.")

if __name__ == '__main__':
    unittest.main()
