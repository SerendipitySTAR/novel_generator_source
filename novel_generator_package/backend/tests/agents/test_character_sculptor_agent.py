import pytest
import unittest
from unittest.mock import AsyncMock, patch

from app.agents.character_sculptor import CharacterSculptorAgent
from app.core.llm import LLMResponse

class TestCharacterSculptorAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = CharacterSculptorAgent(llm=self.mock_llm, project_id="test_project")

    async def test_generate_character_prompt_includes_new_instructions(self):
        # Mock the LLM response
        self.mock_llm.generate_text.return_value = LLMResponse(text='''
        {
          "人物设定": [
            {
              "基本信息": {"姓名": "艾拉"},
              "背景故事": "来自边陲小镇的孤儿。",
              "性格特质": {"核心性格": "勇敢"},
              "能力技能": {"技能": ["剑术"]},
              "内在景观": {
                "动机与目标": {"内心驱动力": "寻求正义", "长期目标": "推翻暴君"},
                "内在冲突与困境": "忠诚与复仇之间的挣扎。",
                "深层动机与潜意识": "害怕孤独，渴望被接纳。"
              },
              "角色弧光": "从单纯的复仇者成长为真正的领袖。",
              "人际关系与动态演变": {
                "初始关系": [{"关系对象": "雷恩", "关系类型": "导师"}],
                "关系演变潜力": [{"关系对象": "雷恩", "演变路径": "从导师变为对手", "触发条件": "理念不合"}]
              }
            }
          ],
          "人物关系图谱": "艾拉与雷恩亦师亦友，后因理念冲突可能反目。"
        }
        =====
        ''')

        # Dummy input data
        input_data = {
            "narrative_concept": "A hero's journey.",
            "world_setting": {"raw_text": "A medieval fantasy world."},
            "plot_outline": {"raw_text": "Chapter 1: Hero starts adventure. Main characters: Ella, Rayn"},
            "num_profiles": 1
        }

        # Spy on the _generate_prompt method to capture the actual prompt string
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Character Sculptor Prompt" # Dummy prompt string for LLM call

            await self.agent.run(input_data)

            # Assert that the LLM was called with the dummy prompt
            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Character Sculptor Prompt",
                temperature=unittest.mock.ANY, # Assuming this comes from settings
                max_tokens=unittest.mock.ANY,  # Assuming this comes from settings
                top_p=unittest.mock.ANY        # Assuming this comes from settings
            )

            # Check the arguments passed to our spy _generate_prompt
            # args[0] is the template string, args[1] is the data dict
            called_prompt_template_str = mock_generate_prompt.call_args[0][0]

            # Verify that the new instructions and keywords are in the prompt template
            self.assertIn("内在景观 (Internal Landscape)", called_prompt_template_str)
            self.assertIn("内在冲突与困境", called_prompt_template_str)
            self.assertIn("深层动机与潜意识", called_prompt_template_str)
            self.assertIn("人际关系与动态演变 (Relationship Dynamics and Evolution)", called_prompt_template_str)
            self.assertIn("关系演变潜力", called_prompt_template_str)

            # Verify that the JSON structure example in the prompt reflects the new fields
            self.assertIn("""\"内在景观\": {
        "动机与目标": {
          "内心驱动力": "...",
          "短期目标": "...",
          "长期目标": "..."
        },
        "内在冲突与困境": "...",
        "深层动机与潜意识": "..."
      }""".replace("  ",""), called_prompt_template_str.replace("  ","")) # Normalize spacing for comparison

            self.assertIn("""\"人际关系与动态演变\": {
        "初始关系": [
          {{"关系对象": "人物2", "关系类型": "...", "关系描述": "..."}},
          {{"关系对象": "人物3", "关系类型": "...", "关系描述": "..."}}
        ],
        "关系演变潜力": [
          {{"关系对象": "人物2", "演变路径": "...", "触发条件": "..."}}
        ]
      }""".replace("  ",""), called_prompt_template_str.replace("  ","")) # Normalize spacing

    async def test_extract_character_names_from_plot_outline(self):
        plot_outline_structured = {
            "章节列表": [
                {"核心内容": {"出场人物": ["Alice", "Bob"]}},
                {"核心内容": {"出场人物": ["Charlie", "Alice"]}}
            ],
            "多线叙事": [
                {"主要人物": ["David", "Bob"]},
                {"主要人物": ["Eve"]}
            ]
        }
        names = self.agent._extract_character_names(plot_outline_structured)
        self.assertCountEqual(names, ["Alice", "Bob", "Charlie", "David", "Eve"])

        plot_outline_raw = {"raw_text": "This is just text."}
        names_raw = self.agent._extract_character_names(plot_outline_raw)
        self.assertEqual(names_raw, [])

if __name__ == '__main__':
    unittest.main()
