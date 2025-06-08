import pytest
import unittest
from unittest.mock import AsyncMock, patch

from app.agents.plot_architect import PlotArchitectAgent
from app.core.llm import LLMResponse

class TestPlotArchitectAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_llm = AsyncMock()
        self.agent = PlotArchitectAgent(llm=self.mock_llm, project_id="test_project")

    async def test_generate_plot_outline_prompt_includes_new_instructions(self):
        # Mock the LLM response (not strictly needed for prompt content check, but good practice)
        self.mock_llm.generate_text.return_value = LLMResponse(text="# 大纲版本1\n## 总体故事结构\nTest Structure")

        # Dummy input data
        input_data = {
            "narrative_concept": "A grand space opera.",
            "world_setting": {"description": "A galaxy far, far away."},
            "conflict_elements": ["Empire vs Rebels"],
            "chapter_count": 20,
            "num_outlines": 1
        }

        # Spy on the _generate_prompt method
        with patch.object(self.agent, '_generate_prompt', new_callable=AsyncMock) as mock_generate_prompt:
            mock_generate_prompt.return_value = "Final Plot Architect Prompt"

            await self.agent.run(input_data)

            self.mock_llm.generate_text.assert_called_once_with(
                prompt="Final Plot Architect Prompt",
                temperature=unittest.mock.ANY,
                max_tokens=unittest.mock.ANY,
                top_p=unittest.mock.ANY
            )

            called_prompt_template_str = mock_generate_prompt.call_args[0][0]

            # Verify new instructional keywords are in the prompt template
            self.assertIn("叙事结构与多线叙事 (Narrative Structure & Multi-Line Narratives)", called_prompt_template_str)
            self.assertIn("情节线交织点", called_prompt_template_str)
            self.assertIn("主题深度 (Thematic Depth)", called_prompt_template_str)
            self.assertIn("核心主题", called_prompt_template_str)
            self.assertIn("主题呈现", called_prompt_template_str)
            self.assertIn("关键情节转折 (Key Plot Twists)", called_prompt_template_str)
            self.assertIn("伏笔铺垫", called_prompt_template_str)

            # Verify new sections in the example output format within the prompt
            self.assertIn("## 叙事结构与多线叙事详情", called_prompt_template_str)
            self.assertIn("### 主线情节", called_prompt_template_str)
            self.assertIn("### 次要情节线1", called_prompt_template_str)
            self.assertIn("## 主题探讨", called_prompt_template_str)
            self.assertIn("## 关键情节转折设计", called_prompt_template_str)
            self.assertIn("### 情节转折点1", called_prompt_template_str)

            # Verify enhanced chapter detail prompts
            self.assertIn("核心事件: [详细内容] (涉及哪些情节线？)", called_prompt_template_str)
            self.assertIn("伏笔/悬念: [详细内容] (为后续哪些情节线或转折铺垫？)", called_prompt_template_str)

    def test_parse_plot_outlines_with_new_sections(self):
        mock_llm_response_text = """
# 大纲版本1
## 总体故事结构
三幕剧结构。

## 章节列表
1. 起点 - 3000字
2. 发展 - 3500字

## 叙事结构与多线叙事详情
### 主线情节
主角A发现神秘遗物，踏上寻找真相之旅。
### 次要情节线1: 追踪者B
反派B奉命追捕主角A，并试图夺取遗物。
B线在第2章与A线交汇。

## 主题探讨
主题是“宿命与自由意志”。通过主角A的选择和反派B的宿命论来体现。

## 关键情节转折设计
### 情节转折点1: 遗物的真相
- 发生章节/时机: 第2章结尾
- 具体描述: 遗物并非宝藏，而是古老诅咒的钥匙。
- 前期伏笔: 第1章中关于遗物的不祥传闻。

## 章节详情
### 第1章: 起点
- 主要场景: 古代遗迹
- 出场人物: 主角A, 老者C
- 核心事件: 主角A从老者C手中获得遗物 (主线)
- 目标与冲突: A要保护遗物，躲避初步追踪
- 关键转折点: 老者C的神秘死亡
- 情感基调: 神秘、紧张
- 伏笔/悬念: 遗物的真正用途？老者C为何被杀？ (为转折点1铺垫)

### 第2章: 发展
- 主要场景: 逃亡之路上的边境小镇
- 出场人物: 主角A, 反派B
- 核心事件: A与B首次正面遭遇，B展示强大实力 (主线, B线交汇)
- 目标与冲突: A艰难摆脱B的追捕
- 关键转折点: 遗物在战斗中意外激活，揭示部分真相 (转折点1发生)
- 情感基调: 惊险、转折
- 伏笔/悬念: 诅咒的具体内容是什么？
        """
        parsed_outlines = self.agent._parse_plot_outlines(mock_llm_response_text)

        self.assertEqual(len(parsed_outlines), 1)
        outline_v1 = parsed_outlines[0]

        self.assertEqual(outline_v1["version"], "1")
        self.assertEqual(outline_v1["structure"], "三幕剧结构。")

        # Test new sections parsing
        self.assertIn("raw_text", outline_v1["narrative_structure_and_plotlines"])
        self.assertIn("主角A发现神秘遗物", outline_v1["narrative_structure_and_plotlines"]["main_plot"])
        self.assertIn("反派B奉命追捕主角A", outline_v1["narrative_structure_and_plotlines"]["subplot_1"])

        self.assertEqual(outline_v1["thematic_depth"], "主题是“宿命与自由意志”。通过主角A的选择和反派B的宿命论来体现。")

        self.assertEqual(len(outline_v1["key_plot_twists"]), 1)
        self.assertEqual(outline_v1["key_plot_twists"][0]["name"], "遗物的真相")
        self.assertIn("遗物并非宝藏", outline_v1["key_plot_twists"][0]["details"])

        # Test chapter list and details (existing functionality, ensure it's not broken)
        self.assertEqual(len(outline_v1["chapters"]), 2)
        self.assertEqual(outline_v1["chapters"][0]["title"], "起点")
        self.assertEqual(len(outline_v1["chapter_details"]), 2)
        self.assertEqual(outline_v1["chapter_details"][0]["title"], "起点")
        self.assertIn("主角A从老者C手中获得遗物", outline_v1["chapter_details"][0]["events"])
        self.assertIn("为转折点1铺垫", outline_v1["chapter_details"][0]["foreshadowing"])
        self.assertIn("主线, B线交汇", outline_v1["chapter_details"][1]["events"])

if __name__ == '__main__':
    unittest.main()
