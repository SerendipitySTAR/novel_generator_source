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
            # Previous assertions for Internal Landscape and Relationship Dynamics should still pass if structure is maintained.
            self.assertIn("内在景观 (Internal Landscape)", called_prompt_template_str)
            self.assertIn("人际关系与动态演变 (Relationship Dynamics and Evolution)", called_prompt_template_str)

            # New assertions for detailed backstories
            self.assertIn("详细背景故事 (Detailed Backstory)", called_prompt_template_str)
            self.assertIn("关键童年/成长经历 (Key Childhood/Formative Experience)", called_prompt_template_str)
            self.assertIn("重大人生转折点 (Major Life Turning Point)", called_prompt_template_str)
            self.assertIn("核心秘密/未解之谜 (Core Secret/Unresolved Mystery)", called_prompt_template_str)
            self.assertIn("背景故事与潜在情节钩子 (Backstory & Potential Plot Hooks)", called_prompt_template_str)

            # New assertions for plot-relevant skills
            self.assertIn("请确保这些技能与小说的主题、世界观或预期冲突类型相关。", called_prompt_template_str)
            self.assertIn("为每项主要技能简述其在故事中可能的应用场景或如何帮助角色克服挑战。", called_prompt_template_str)

            # New assertions for plot-relevant flaws (within "性格特质")
            self.assertIn("对于主要**缺点 (Flaws/Shortcomings)**，请思考它们如何不仅仅是性格缺陷", called_prompt_template_str)
            self.assertIn("简述其可能如何引发冲突或使角色陷入困境", called_prompt_template_str)

            # Verify that the JSON structure example in the prompt reflects the new detailed fields

            # Check for detailed backstory in JSON example
            self.assertIn("""\"背景故事\": {
        "关键童年经历": "...",
        "重大人生转折点": "...",
        "核心秘密": "...",
        "情节钩子": "..."
      }""".replace("  ",""), called_prompt_template_str.replace("  ",""))

            # Check for plot-relevant flaws in JSON example (within "性格特质")
            self.assertIn(""""缺点": [
          {{"缺陷": "过度自信", "情节关联": "可能导致其在关键时刻低估敌人，造成失败。"}},
          "..."
        ]""".replace("  ",""), called_prompt_template_str.replace("  ",""))

            # Check for plot-relevant skills in JSON example (within "能力技能")
            self.assertIn(""""技能": [
          {{"技能名称": "精准射击", "描述": "百步穿杨的弓箭手。", "情节关联": "在远程战斗或需要精确操作的场合发挥关键作用，例如射中远处的机关。"}},
          "..."
        ]""".replace("  ",""), called_prompt_template_str.replace("  ",""))

            # Verify existing JSON examples are still there (or updated)
            # This one for "内在景观" was already checked in a previous version of this test, ensure it's still valid.
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
