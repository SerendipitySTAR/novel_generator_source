"""
编排与流程控制层，基于LangGraph实现
"""
from typing import Dict, List, Optional, Any, Union
from langchain.graphs import StateGraph
from langchain.graphs.graph import END
import uuid
from app.config import settings

class NovelWorkflow:
    """小说生成工作流控制器"""
    
    def __init__(self, project_id: str):
        """
        初始化工作流控制器
        
        Args:
            project_id: 项目ID
        """
        self.project_id = project_id
        self.workflow = self._build_workflow()
        self.current_state = "start"
        self.state_data = {
            "project_id": project_id,
            "user_inputs": {},
            "generated_outputs": {},
            "selected_outputs": {},
            "current_chapter": 1,
            "max_chapters": 10,  # 默认章节数，可由用户修改
            "cumulative_quality_scores": [], # Initialize new field
            "current_chapter_quality": None, # Placeholder for quality score
            "current_chapter_feedback": None, # Placeholder for feedback
            "current_chapter_transition_score": None, # Placeholder for transition score
        }
    
    # Placeholder Node Implementations
    def _assess_chapter_transition(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder node for assessing chapter transition quality."""
        print("Workflow Node: _assess_chapter_transition - Chapter transition assessment would happen here.")
        # Simulate transition assessment
        state_data['current_chapter_transition_score'] = 0.85  # Example placeholder score
        # In a real scenario, this might involve calling an agent:
        # transition_assessment = await some_agent.run(
        #     previous_chapter_content=state_data.get('previous_chapter_content'),
        #     current_chapter_content=state_data.get('current_generated_chapter_content')
        # )
        # state_data['current_chapter_transition_score'] = transition_assessment.get('score')
        # state_data['current_chapter_transition_feedback'] = transition_assessment.get('feedback')
        return state_data

    def _update_cumulative_quality_scores(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Node to update cumulative quality scores for chapters."""
        print("Workflow Node: _update_cumulative_quality_scores - Updating cumulative quality scores.")
        current_chapter_num = state_data.get('current_chapter', 0)
        # Assuming 'current_chapter_quality' and 'current_chapter_feedback' are populated by 'evaluate_chapter' or 'polish_chapter'
        quality_score = state_data.get('current_chapter_quality', 'N/A')
        feedback = state_data.get('current_chapter_feedback', 'N/A')

        # Ensure 'cumulative_quality_scores' list exists
        if 'cumulative_quality_scores' not in state_data:
            state_data['cumulative_quality_scores'] = []

        state_data['cumulative_quality_scores'].append({
            "chapter_number": current_chapter_num,
            "quality_score": quality_score,
            "feedback": feedback,
            "transition_score": state_data.get('current_chapter_transition_score', 'N/A') # Also log transition score
        })
        print(f"Cumulative scores: {state_data['cumulative_quality_scores']}")
        return state_data

    def _check_long_term_consistency(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder node for checking long-term plot consistency."""
        print("Workflow Node: _check_long_term_consistency - Long-term consistency check would happen here.")
        # In a real scenario, this would call an agent:
        # consistency_report = await some_consistency_agent.run(
        #     all_chapters=state_data.get('all_chapters_data'),
        #     world_setting=state_data.get('selected_world_setting_content'),
        #     plot_outline=state_data.get('selected_plot_outline_content'),
        #     long_term_summary=state_data.get('long_term_summary_from_context_agent')
        # )
        # state_data['last_consistency_check_report'] = consistency_report
        return state_data

    def _build_workflow(self) -> StateGraph:
        """
        构建工作流图
        
        Returns:
            StateGraph: 工作流图
        """
        # 创建工作流图
        workflow = StateGraph("novel_generation")
        
        # 添加节点
        workflow.add_node("start", {})
        workflow.add_node("generate_concepts", {})
        workflow.add_node("select_concept", {})
        workflow.add_node("expand_concept", {})
        workflow.add_node("generate_world_settings", {})
        workflow.add_node("select_world_setting", {})
        workflow.add_node("generate_plot_outlines", {})
        workflow.add_node("select_plot_outline", {})
        workflow.add_node("generate_characters", {})
        workflow.add_node("select_characters", {})
        workflow.add_node("initialize_knowledge_base", {})
        workflow.add_node("chapter_loop_start", {})
        workflow.add_node("generate_summary", {})
        workflow.add_node("check_plot_branch", {})
        workflow.add_node("generate_plot_branches", {})
        workflow.add_node("select_plot_branch", {})
        workflow.add_node("generate_chapter", {})
        workflow.add_node("assess_chapter_transition", self._assess_chapter_transition) # New Node
        workflow.add_node("evaluate_chapter", {})
        workflow.add_node("retry_chapter", {})
        workflow.add_node("user_edit_chapter", {})
        workflow.add_node("polish_chapter", {})
        workflow.add_node("update_cumulative_scores", self._update_cumulative_quality_scores) # New Node
        workflow.add_node("update_knowledge_base", {})
        workflow.add_node("check_long_term_consistency", self._check_long_term_consistency) # New Node
        workflow.add_node("check_more_chapters", {})
        workflow.add_node("complete_novel", {})
        
        # 添加边
        workflow.add_edge("start", "generate_concepts")
        workflow.add_edge("generate_concepts", "select_concept")
        workflow.add_conditional_edges(
            "select_concept",
            lambda x: "expand" if x.get("expand_concept", False) else "skip_expand",
            {
                "expand": "expand_concept",
                "skip_expand": "generate_world_settings"
            }
        )
        workflow.add_edge("expand_concept", "generate_world_settings")
        workflow.add_edge("generate_world_settings", "select_world_setting")
        workflow.add_edge("select_world_setting", "generate_plot_outlines")
        workflow.add_edge("generate_plot_outlines", "select_plot_outline")
        workflow.add_edge("select_plot_outline", "generate_characters")
        workflow.add_edge("generate_characters", "select_characters")
        workflow.add_edge("select_characters", "initialize_knowledge_base")
        workflow.add_edge("initialize_knowledge_base", "chapter_loop_start")
        workflow.add_edge("chapter_loop_start", "generate_summary")
        workflow.add_edge("generate_summary", "check_plot_branch")
        workflow.add_conditional_edges(
            "check_plot_branch",
            lambda x: "branch" if x.get("is_key_plot_point", False) else "no_branch",
            {
                "branch": "generate_plot_branches",
                "no_branch": "generate_chapter"
            }
        )
        workflow.add_edge("generate_plot_branches", "select_plot_branch")
        workflow.add_edge("select_plot_branch", "generate_chapter")

        # Modified Edges for new nodes
        workflow.add_edge("generate_chapter", "assess_chapter_transition")
        workflow.add_edge("assess_chapter_transition", "evaluate_chapter")

        workflow.add_conditional_edges(
            "evaluate_chapter",
            lambda x: self._evaluate_chapter_decision(x),
            {
                "retry": "retry_chapter",
                "user_edit": "user_edit_chapter",
                "accept": "polish_chapter" # Accepted chapters go to polish (or directly to update scores if polish is skipped)
            }
        )
        workflow.add_edge("retry_chapter", "generate_chapter")
        workflow.add_edge("user_edit_chapter", "polish_chapter")

        # If polish_chapter is chosen or skipped, it goes to update_cumulative_scores
        workflow.add_conditional_edges(
            "polish_chapter",
            lambda x: "polish" if x.get("polish_chapter_needed", True) else "skip_polish", # Assuming a flag like 'polish_chapter_needed'
            {
                "polish": "update_cumulative_scores", # Actual polishing would happen then update scores
                "skip_polish": "update_cumulative_scores" # Skip polish, directly update scores
            }
        )
        # Edge from update_cumulative_scores to update_knowledge_base
        workflow.add_edge("update_cumulative_scores", "update_knowledge_base")

        # Modified Edges for new node
        workflow.add_edge("update_knowledge_base", "check_long_term_consistency")
        workflow.add_edge("check_long_term_consistency", "check_more_chapters")

        workflow.add_conditional_edges(
            "check_more_chapters",
            lambda x: "more_chapters" if self._has_more_chapters(x) else "complete",
            {
                "more_chapters": "chapter_loop_start",
                "complete": "complete_novel"
            }
        )
        workflow.add_edge("complete_novel", END)
        
        # 设置起始节点
        workflow.set_entry_point("start")
        
        return workflow
    
    def _evaluate_chapter_decision(self, state_data: Dict[str, Any]) -> str:
        """
        根据章节评分决定下一步操作
        
        Args:
            state_data: 状态数据
            
        Returns:
            str: 决策结果，retry/user_edit/accept
        """
        score = state_data.get("chapter_score", 0)
        retry_count = state_data.get("retry_count", 0)
        
        if score < settings.QUALITY_THRESHOLD and retry_count < settings.MAX_RETRIES:
            return "retry"
        elif score < settings.QUALITY_THRESHOLD:
            return "user_edit"
        else:
            return "accept"
    
    def _has_more_chapters(self, state_data: Dict[str, Any]) -> bool:
        """
        检查是否还有更多章节需要生成
        
        Args:
            state_data: 状态数据
            
        Returns:
            bool: 是否还有更多章节
        """
        current_chapter = state_data.get("current_chapter", 1)
        max_chapters = state_data.get("max_chapters", 10)
        return current_chapter < max_chapters
    
    async def run_step(self, step_name: str, step_input: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行工作流的一个步骤
        
        Args:
            step_name: 步骤名称
            step_input: 步骤输入
            
        Returns:
            Dict[str, Any]: 步骤输出
        """
        # 更新状态数据
        if step_input:
            self.state_data.update(step_input)
        
        # 检查步骤是否存在
        if step_name not in self.workflow.nodes:
            raise ValueError(f"步骤 {step_name} 不存在")
        
        # 更新当前状态
        self.current_state = step_name
        
        # 根据步骤名称执行相应的操作
        # 在实际应用中，这里应该调用相应的智能体
        # 这里只是一个简单的实现，实际应用中需要更复杂的逻辑
        result = {}
        
        # 返回结果
        return result
    
    async def get_next_steps(self) -> List[str]:
        """
        获取当前状态的下一步可能的步骤
        
        Returns:
            List[str]: 下一步可能的步骤列表
        """
        # 在实际应用中，这里应该根据工作流图和当前状态计算下一步可能的步骤
        # 这里只是一个简单的实现
        if self.current_state == "start":
            return ["generate_concepts"]
        elif self.current_state == "generate_concepts":
            return ["select_concept"]
        # ... 其他状态的下一步
        
        return []
