import pytest
import unittest
from unittest.mock import AsyncMock, patch

from app.agents.world_weaver import WorldWeaverAgent
from app.core.llm import LLMResponse

class TestWorldWeaverAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = WorldWeaverAgent(llm=self.mock_llm, project_id="test_project")

    async def test_generate_world_setting_prompt_includes_new_instructions(self):
        # Mock the LLM response
        self.mock_llm.generate_text.return_value = LLMResponse(text="# 世界观1：测试特色\n## 基础设定\nTest Basic Setting")

        # Dummy input data
        input_data = {
            "narrative_concept": "A tale of ancient magic and lost technology.",
            "num_settings": 1
        }

        # Spy on the _generate_prompt method
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final World Weaver Prompt"

            await self.agent.run(input_data)

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final World Weaver Prompt",
                temperature=unittest.mock.ANY,
                max_tokens=unittest.mock.ANY,
                top_p=unittest.mock.ANY
            )

            called_prompt_template_str = mock_generate_prompt.call_args[0][0]

            # Verify new detailed instructions in the prompt template
            # For "地理环境" (Geographical Environment)
            self.assertIn("环境互动", called_prompt_template_str)
            self.assertIn("特定地理特征（如险峻山脉、巨大森林、资源匮乏的沙漠、特殊天象等）如何成为故事中潜在的机遇、挑战或象征", called_prompt_template_str)

            # For "历史背景与传说" (Historical Background & Legends)
            self.assertIn("关键历史时期", called_prompt_template_str)
            self.assertIn("传说与神话", called_prompt_template_str)
            self.assertIn("解释这个故事如何影响当前人们的信仰、价值观或社会习俗", called_prompt_template_str)
            self.assertIn("被遗忘或争议的历史", called_prompt_template_str)
            self.assertIn("这些片段可能在故事后续中变得重要或揭示某些真相", called_prompt_template_str)

            # For "文化与社会" (Culture & Society)
            self.assertIn("主要种族及其特征、语言体系", called_prompt_template_str)
            self.assertIn("社会结构", called_prompt_template_str) # Existing, but good to confirm
            self.assertIn("阶级划分、权力结构、主要社会矛盾或冲突点", called_prompt_template_str)
            self.assertIn("核心价值观与信仰", called_prompt_template_str) # Existing, but good to confirm
            self.assertIn("主流的价值观念、宗教信仰或哲学思想", called_prompt_template_str)
            self.assertIn("文化习俗与艺术", called_prompt_template_str)
            self.assertIn("例如，独特的节日、成人仪式、婚姻制度、丧葬习俗、社交礼仪、以及具有代表性的艺术形式（音乐、舞蹈、雕塑、绘画等）或娱乐活动", called_prompt_template_str)

            # For "特殊生物/物种" (Special Creatures/Species)
            self.assertIn("与主要种族/人类的关系（如共生、敌对、被奴役、被崇拜等）", called_prompt_template_str)

    def test_parse_world_settings(self):
        # Test the existing parser to ensure it still works and captures content under sections
        mock_llm_text = """
# 世界观1：魔法与蒸汽的交融
## 基础设定
宇宙遵循标准物理定律，但存在一种名为“以太”的能量。
## 地理环境
主要大陆为“艾奥尼亚”，中央是巨大的“蒸汽山脉”。
环境互动示例：蒸汽山脉是重要资源点，也是冲突焦点。
## 历史背景与传说
关键历史时期：大分裂时代 - 各城邦因以太利用方式不同而分裂。
传说：火鸟传说 - 火鸟带来以太，其眼泪能净化土地。此传说让人们敬畏火山。
争议历史：古代文明是否因滥用以太而毁灭。
## 文化与社会
主要种族：人类，矮人。
社会结构：城邦联盟，技术工会权力大。
核心价值观：创新、实用。
文化习俗与艺术：每年有“蒸汽节”庆祝新技术发明。艺术多为机械风格。
## 特殊生物/物种
飞空水母：被用作小型运输工具。
        """
        parsed_settings = self.agent._parse_world_settings(mock_llm_text)
        self.assertEqual(len(parsed_settings), 1)
        setting = parsed_settings[0]
        self.assertEqual(setting["description"], "魔法与蒸汽的交融")

        self.assertIn("基础设定", setting["sections"])
        self.assertIn("宇宙遵循标准物理定律", setting["sections"]["基础设定"])

        self.assertIn("地理环境", setting["sections"])
        self.assertIn("环境互动示例：蒸汽山脉是重要资源点", setting["sections"]["地理环境"])

        self.assertIn("历史背景与传说", setting["sections"])
        self.assertIn("大分裂时代", setting["sections"]["历史背景与传说"])
        self.assertIn("火鸟传说", setting["sections"]["历史背景与传说"])
        self.assertIn("争议历史：古代文明是否因滥用以太而毁灭", setting["sections"]["历史背景与传说"])

        self.assertIn("文化与社会", setting["sections"])
        self.assertIn("每年有“蒸汽节”", setting["sections"]["文化与社会"])

        self.assertIn("特殊生物/物种", setting["sections"])
        self.assertIn("飞空水母", setting["sections"]["特殊生物/物种"])

if __name__ == '__main__':
    unittest.main()
