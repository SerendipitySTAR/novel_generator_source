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
            self.assertIn("有故事潜力的特色动植物 (Distinctive Flora/Fauna with Story Potential)", called_prompt_template_str)

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
            self.assertIn("主流的价值观念、宗教信仰或哲学思想", called_prompt_template_str) # Part of Core Beliefs/Pantheon
            self.assertIn("核心价值观与信仰体系 (Main Beliefs/Pantheon)", called_prompt_template_str)
            self.assertIn("创世神话或核心宇宙观", called_prompt_template_str)
            self.assertIn("主要经济活动与资源 (Main Economic Activities & Resources)", called_prompt_template_str)
            self.assertIn("文化习俗与艺术", called_prompt_template_str)
            self.assertIn("例如，独特的节日、成人仪式、婚姻制度、丧葬习俗、社交礼仪、以及具有代表性的艺术形式（音乐、舞蹈、雕塑、绘画等）或娱乐活动", called_prompt_template_str)

            # For "特殊生物/物种" (Special Creatures/Species)
            self.assertIn("与主要种族/人类的关系（如共生、敌对、被奴役、被崇拜等）", called_prompt_template_str)
            self.assertIn("它们在生态系统或文化中的独特角色", called_prompt_template_str)

            # General Interconnectivity instruction
            self.assertIn("重要总体要求：** 在描述以下各个方面时，请始终思考它们之间的**相互联系**", called_prompt_template_str)
            # Section-specific interconnectivity instruction (check one example)
            self.assertTrue(called_prompt_template_str.count("请说明此方面如何与世界观中的至少另外两个主要方面相互关联和影响。") >= 7) # Should appear for each of the 7 main sections

            # For "核心世界魅力点 (Core World 'Wow Factors')"
            self.assertIn("核心世界魅力点 (Core World 'Wow Factors')", called_prompt_template_str)
            self.assertIn("描述2-3个使这个世界真正独特且令人难忘的方面", called_prompt_template_str)
            self.assertIn("解释为什么这些元素具有吸引力，以及它们可能为故事带来的潜力", called_prompt_template_str)

            # Check example output format update
            self.assertIn("## 核心世界魅力点 (Core World 'Wow Factors')\n        [详细内容]", called_prompt_template_str)


    def test_parse_world_settings(self):
        mock_llm_text = """
# 世界观1：魔法与蒸汽的交融
## 基础设定
宇宙遵循标准物理定律，但存在一种名为“以太”的能量。
此方面与能量体系和历史背景相关。
## 地理环境
主要大陆为“艾奥尼亚”，中央是巨大的“蒸汽山脉”。
环境互动示例：蒸汽山脉是重要资源点，也是冲突焦点。
特色动植物：蒸汽菇，能在高热环境生长，是矮人的主要食物来源。
此方面与文化社会（矮人饮食）和经济（资源）相关。
## 历史背景与传说
关键历史时期：大分裂时代 - 各城邦因以太利用方式不同而分裂。
传说：火鸟传说 - 火鸟带来以太，其眼泪能净化土地。此传说让人们敬畏火山。
争议历史：古代文明是否因滥用以太而毁灭。
此方面与主要势力（分裂的城邦）和能量体系（以太利用）相关。
## 文化与社会
主要种族：人类，矮人。语言：通用语，矮人语。
社会结构：城邦联盟，技术工会权力大。
核心价值观与信仰体系：信仰创造之神“工匠”，创世神话讲述世界由巨大机械构成。主要经济活动为矿石开采和蒸汽机械制造。
文化习俗与艺术：每年有“蒸汽节”庆祝新技术发明。艺术多为机械风格。
此方面与地理环境（矿石）和能量体系（蒸汽技术）相关。
## 特殊生物/物种
飞空水母：被用作小型运输工具。与人类关系为工具性利用。
此方面与经济（运输）和科技水平（利用方式）相关。
## 核心世界魅力点 (Core World 'Wow Factors')
1. 浮空岛屿城市：依靠古老技术悬浮，成为各种族中立区。
2. 周期性以太风暴：会暂时扰乱魔法和科技，带来机遇与危险。
        """
        parsed_settings = self.agent._parse_world_settings(mock_llm_text)
        self.assertEqual(len(parsed_settings), 1)
        setting = parsed_settings[0]
        self.assertEqual(setting["description"], "魔法与蒸汽的交融")

        self.assertIn("基础设定", setting["sections"])
        self.assertIn("宇宙遵循标准物理定律", setting["sections"]["基础设定"])

        self.assertIn("地理环境", setting["sections"])
        self.assertIn("环境互动示例：蒸汽山脉是重要资源点", setting["sections"]["地理环境"])
        self.assertIn("特色动植物：蒸汽菇", setting["sections"]["地理环境"]) # Check for new detail

        self.assertIn("历史背景与传说", setting["sections"])
        self.assertIn("大分裂时代", setting["sections"]["历史背景与传说"])
        self.assertIn("火鸟传说", setting["sections"]["历史背景与传说"])
        self.assertIn("争议历史：古代文明是否因滥用以太而毁灭", setting["sections"]["历史背景与传说"])

        self.assertIn("文化与社会", setting["sections"])
        self.assertIn("每年有“蒸汽节”", setting["sections"]["文化与社会"])
        self.assertIn("创世神话讲述世界由巨大机械构成", setting["sections"]["文化与社会"]) # Check for new detail (cosmology)
        self.assertIn("主要经济活动为矿石开采和蒸汽机械制造", setting["sections"]["文化与社会"]) # Check for new detail (economy)

        self.assertIn("特殊生物/物种", setting["sections"])
        self.assertIn("飞空水母", setting["sections"]["特殊生物/物种"])

        # Check for new "core_wow_factors" key and content
        self.assertIn("core_wow_factors", setting)
        self.assertIn("浮空岛屿城市", setting["core_wow_factors"])
        self.assertIn("周期性以太风暴", setting["core_wow_factors"])
        # Ensure it's removed from general sections if parsed specifically
        self.assertNotIn("核心世界魅力点 (Core World 'Wow Factors')", setting["sections"])
        self.assertNotIn("核心世界魅力点", setting["sections"])


if __name__ == '__main__':
    unittest.main()
