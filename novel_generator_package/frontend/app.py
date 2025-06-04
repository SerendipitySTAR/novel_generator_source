"""
前端界面入口文件
"""
import streamlit as st
import requests
import json
import time

# API基础URL
API_BASE_URL = "http://localhost:8002/api"

# 页面配置
st.set_page_config(
    page_title="自动小说生成器",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 会话状态初始化
if "project_id" not in st.session_state:
    st.session_state.project_id = None
if "step" not in st.session_state:
    st.session_state.step = "start"
if "concepts" not in st.session_state:
    st.session_state.concepts = []
if "world_settings" not in st.session_state:
    st.session_state.world_settings = []
if "plot_outlines" not in st.session_state:
    st.session_state.plot_outlines = []
if "character_profiles" not in st.session_state:
    st.session_state.character_profiles = []
if "chapters" not in st.session_state:
    st.session_state.chapters = {}
if "request_id" not in st.session_state:
    st.session_state.request_id = None

# 标题和介绍
st.title("📚 自动小说生成器")
st.markdown("""
这是一个基于多智能体协作的全自动多轮交互式小说生成器。通过简单的输入和选择，
您可以创建一个完整的小说，包括核心创意、世界观设定、人物设定、章节内容等。
""")

# 侧边栏 - 项目状态
with st.sidebar:
    st.header("项目状态")
    if st.session_state.project_id:
        st.success(f"项目ID: {st.session_state.project_id}")
        st.info(f"当前步骤: {st.session_state.step}")
        
        # 显示已完成的步骤
        if st.session_state.step != "start":
            st.subheader("已完成步骤")
            steps = ["创建项目", "生成概述", "选择概述", "生成世界观", "选择世界观", 
                    "生成大纲", "选择大纲", "生成人物设定", "选择人物设定"]
            current_step_index = steps.index(st.session_state.step) if st.session_state.step in steps else len(steps)
            for i, step in enumerate(steps):
                if i < current_step_index:
                    st.success(f"✅ {step}")
                elif i == current_step_index:
                    st.info(f"🔄 {step}")
                else:
                    st.text(f"⏳ {step}")
        
        # 重置按钮
        if st.button("重置项目"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.step = "start"
            st.session_state.project_id = None
            st.experimental_rerun()
    else:
        st.warning("尚未创建项目")

# 主界面 - 根据当前步骤显示不同内容
if st.session_state.step == "start":
    # 创建新项目
    st.header("创建新项目")
    if st.button("开始创建"):
        with st.spinner("正在创建项目..."):
            try:
                response = requests.post(f"{API_BASE_URL}/projects")
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.project_id = data["project_id"]
                    st.session_state.step = "input_prompt"
                    st.success("项目创建成功！")
                    st.experimental_rerun()
                else:
                    st.error(f"创建项目失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "input_prompt":
    # 输入提示词
    st.header("输入创意提示")
    st.markdown("""
    请输入您的小说创意提示，描述您想要的小说类型、主题、风格等。
    例如："一个发生在未来太空殖民地的悬疑故事，涉及人工智能叛变和人类生存"
    """)
    
    prompt = st.text_area("创意提示", height=150)
    style = st.selectbox("风格偏好", ["不指定", "科幻", "奇幻", "悬疑", "恐怖", "爱情", "历史", "冒险"])
    
    if st.button("生成概述"):
        if not prompt:
            st.warning("请输入创意提示")
        else:
            with st.spinner("正在生成小说概述..."):
                try:
                    payload = {
                        "prompt": prompt,
                        "style_preference": style if style != "不指定" else None
                    }
                    response = requests.post(f"{API_BASE_URL}/generate-concepts", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.concepts = data["concepts"]
                        st.session_state.request_id = data["request_id"]
                        st.session_state.step = "select_concept"
                        st.success("概述生成成功！")
                        st.experimental_rerun()
                    else:
                        st.error(f"生成概述失败: {response.text}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "select_concept":
    # 选择概述
    st.header("选择小说概述")
    st.markdown("请从以下生成的概述中选择一个您喜欢的：")
    
    selected_concept = None
    for i, concept in enumerate(st.session_state.concepts):
        with st.expander(f"概述 {i+1}", expanded=True):
            st.markdown(concept)
            if st.button(f"选择概述 {i+1}", key=f"concept_{i}"):
                selected_concept = i
    
    if selected_concept is not None:
        with st.spinner("正在处理您的选择..."):
            try:
                payload = {
                    "concept_id": selected_concept,
                    "request_id": st.session_state.request_id
                }
                response = requests.post(f"{API_BASE_URL}/select-concept", json=payload)
                if response.status_code == 200:
                    # 扩展概述
                    expand_response = requests.post(f"{API_BASE_URL}/expand-concept", json=payload)
                    if expand_response.status_code == 200:
                        expand_data = expand_response.json()
                        st.session_state.expanded_concept = expand_data["expanded_concept"]
                        st.session_state.step = "generate_world"
                        st.success("概述已选择并扩展！")
                        st.experimental_rerun()
                    else:
                        st.error(f"扩展概述失败: {expand_response.text}")
                else:
                    st.error(f"选择概述失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "generate_world":
    # 显示扩展后的概述
    st.header("扩展后的小说概述")
    with st.expander("查看扩展后的概述", expanded=True):
        st.markdown(st.session_state.expanded_concept)
    
    # 生成世界观
    st.header("生成世界观设定")
    if st.button("生成世界观"):
        with st.spinner("正在生成世界观设定..."):
            try:
                payload = {
                    "concept_id": 0,  # 使用第一个概述（已经选择并扩展）
                    "request_id": st.session_state.request_id
                }
                response = requests.post(f"{API_BASE_URL}/generate-world-settings", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.world_settings = data["world_settings"]
                    st.session_state.step = "select_world"
                    st.success("世界观设定生成成功！")
                    st.experimental_rerun()
                else:
                    st.error(f"生成世界观设定失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "select_world":
    # 选择世界观
    st.header("选择世界观设定")
    st.markdown("请从以下生成的世界观设定中选择一个您喜欢的：")
    
    selected_world = None
    for i, world_setting in enumerate(st.session_state.world_settings):
        with st.expander(f"世界观 {i+1}", expanded=True):
            # 显示世界观设定（可能需要格式化）
            if "raw_text" in world_setting:
                st.markdown(world_setting["raw_text"])
            else:
                st.json(world_setting)
            if st.button(f"选择世界观 {i+1}", key=f"world_{i}"):
                selected_world = i
    
    if selected_world is not None:
        with st.spinner("正在处理您的选择..."):
            try:
                payload = {
                    "world_setting_id": selected_world,
                    "request_id": st.session_state.request_id
                }
                response = requests.post(f"{API_BASE_URL}/select-world-setting", json=payload)
                if response.status_code == 200:
                    st.session_state.step = "generate_plot"
                    st.success("世界观设定已选择！")
                    st.experimental_rerun()
                else:
                    st.error(f"选择世界观设定失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "generate_plot":
    # 生成大纲
    st.header("生成小说大纲")
    if st.button("生成大纲"):
        with st.spinner("正在生成小说大纲..."):
            try:
                payload = {
                    "world_setting_id": 0,  # 使用第一个世界观（已经选择）
                    "request_id": st.session_state.request_id
                }
                response = requests.post(f"{API_BASE_URL}/generate-plot-outlines", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.plot_outlines = data["plot_outlines"]
                    st.session_state.step = "select_plot"
                    st.success("小说大纲生成成功！")
                    st.experimental_rerun()
                else:
                    st.error(f"生成小说大纲失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "select_plot":
    # 选择大纲
    st.header("选择小说大纲")
    st.markdown("请从以下生成的小说大纲中选择一个您喜欢的：")
    
    selected_plot = None
    for i, plot_outline in enumerate(st.session_state.plot_outlines):
        with st.expander(f"大纲 {i+1}", expanded=True):
            # 显示大纲（可能需要格式化）
            if "raw_text" in plot_outline:
                st.markdown(plot_outline["raw_text"])
            else:
                st.subheader(f"故事结构: {plot_outline.get('故事结构', '未指定')}")
                
                # 显示章节列表
                if "章节列表" in plot_outline:
                    st.subheader("章节列表")
                    for chapter in plot_outline["章节列表"]:
                        with st.expander(f"第{chapter['章节号']}章: {chapter['标题']} (约{chapter['预计字数']}字)"):
                            if "核心内容" in chapter:
                                st.markdown(f"**主要场景**: {', '.join(chapter['核心内容'].get('主要场景', []))}")
                                st.markdown(f"**出场人物**: {', '.join(chapter['核心内容'].get('出场人物', []))}")
                                st.markdown(f"**核心事件**: {chapter['核心内容'].get('核心事件', '')}")
                                st.markdown(f"**目标与冲突**: {chapter['核心内容'].get('目标与冲突', '')}")
                                st.markdown(f"**关键转折点**: {chapter['核心内容'].get('关键转折点', '')}")
                                st.markdown(f"**情感基调**: {chapter['核心内容'].get('情感基调', '')}")
                                st.markdown(f"**伏笔或悬念**: {chapter['核心内容'].get('伏笔或悬念', '')}")
                
                # 显示多线叙事
                if "多线叙事" in plot_outline:
                    st.subheader("多线叙事")
                    for storyline in plot_outline["多线叙事"]:
                        st.markdown(f"**{storyline['故事线名称']}**")
                        st.markdown(f"涉及章节: {', '.join(map(str, storyline['涉及章节']))}")
                        st.markdown(f"主要人物: {', '.join(storyline['主要人物'])}")
                        st.markdown(f"核心冲突: {storyline['核心冲突']}")
            
            if st.button(f"选择大纲 {i+1}", key=f"plot_{i}"):
                selected_plot = i
    
    if selected_plot is not None:
        with st.spinner("正在处理您的选择..."):
            try:
                payload = {
                    "plot_outline_id": selected_plot,
                    "request_id": st.session_state.request_id
                }
                response = requests.post(f"{API_BASE_URL}/select-plot-outline", json=payload)
                if response.status_code == 200:
                    st.session_state.step = "generate_characters"
                    st.success("小说大纲已选择！")
                    st.experimental_rerun()
                else:
                    st.error(f"选择小说大纲失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "generate_characters":
    # 生成人物设定
    st.header("生成人物设定")
    if st.button("生成人物设定"):
        with st.spinner("正在生成人物设定..."):
            try:
                payload = {
                    "plot_outline_id": 0,  # 使用第一个大纲（已经选择）
                    "request_id": st.session_state.request_id
                }
                response = requests.post(f"{API_BASE_URL}/generate-character-profiles", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.character_profiles = data["character_profiles"]
                    st.session_state.step = "select_characters"
                    st.success("人物设定生成成功！")
                    st.experimental_rerun()
                else:
                    st.error(f"生成人物设定失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "select_characters":
    # 选择人物设定
    st.header("选择人物设定")
    st.markdown("请从以下生成的人物设定中选择一个您喜欢的：")
    
    selected_characters = None
    for i, character_profile in enumerate(st.session_state.character_profiles):
        with st.expander(f"人物设定 {i+1}", expanded=True):
            # 显示人物设定（可能需要格式化）
            if "raw_text" in character_profile:
                st.markdown(character_profile["raw_text"])
            else:
                if "人物设定" in character_profile:
                    for character in character_profile["人物设定"]:
                        if "基本信息" in character:
                            st.subheader(f"{character['基本信息'].get('姓名', '无名')}")
                            st.markdown(f"**性别**: {character['基本信息'].get('性别', '')}")
                            st.markdown(f"**年龄**: {character['基本信息'].get('年龄', '')}")
                            st.markdown(f"**种族**: {character['基本信息'].get('种族', '')}")
                            st.markdown(f"**外貌特征**: {', '.join(character['基本信息'].get('外貌特征', []))}")
                            st.markdown(f"**衣着风格**: {character['基本信息'].get('衣着风格', '')}")
                        
                        if "背景故事" in character:
                            st.markdown(f"**背景故事**: {character['背景故事']}")
                        
                        if "性格特质" in character:
                            st.markdown("**性格特质**:")
                            st.markdown(f"核心性格: {character['性格特质'].get('核心性格', '')}")
                            st.markdown(f"价值观: {character['性格特质'].get('价值观', '')}")
                            st.markdown(f"优点: {', '.join(character['性格特质'].get('优点', []))}")
                            st.markdown(f"缺点: {', '.join(character['性格特质'].get('缺点', []))}")
                            st.markdown(f"癖好: {character['性格特质'].get('癖好', '')}")
                            st.markdown(f"口头禅: {character['性格特质'].get('口头禅', '')}")
                        
                        if "动机与目标" in character:
                            st.markdown("**动机与目标**:")
                            st.markdown(f"内心驱动力: {character['动机与目标'].get('内心驱动力', '')}")
                            st.markdown(f"短期目标: {character['动机与目标'].get('短期目标', '')}")
                            st.markdown(f"长期目标: {character['动机与目标'].get('长期目标', '')}")
                        
                        if "角色弧光" in character:
                            st.markdown(f"**角色弧光**: {character['角色弧光']}")
                        
                        st.markdown("---")
                
                if "人物关系图谱" in character_profile:
                    st.subheader("人物关系图谱")
                    st.markdown(character_profile["人物关系图谱"])
            
            if st.button(f"选择人物设定 {i+1}", key=f"characters_{i}"):
                selected_characters = i
    
    if selected_characters is not None:
        with st.spinner("正在处理您的选择..."):
            try:
                payload = {
                    "character_profiles_id": selected_characters,
                    "request_id": st.session_state.request_id
                }
                response = requests.post(f"{API_BASE_URL}/select-character-profiles", json=payload)
                if response.status_code == 200:
                    st.session_state.step = "generate_chapters"
                    st.success("人物设定已选择！")
                    st.experimental_rerun()
                else:
                    st.error(f"选择人物设定失败: {response.text}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

elif st.session_state.step == "generate_chapters":
    # 生成章节
    st.header("生成小说章节")
    
    # 获取选定的大纲
    selected_plot_outline = None
    response = requests.get(f"{API_BASE_URL}/projects/{st.session_state.request_id}")
    if response.status_code == 200:
        data = response.json()
        if "data" in data and "selected_plot_outline" in data["data"]:
            selected_plot_outline = data["data"]["selected_plot_outline"]
    
    if selected_plot_outline and "章节列表" in selected_plot_outline:
        st.subheader("章节列表")
        
        # 显示章节列表和生成按钮
        for chapter in selected_plot_outline["章节列表"]:
            chapter_id = chapter["章节号"]
            chapter_title = chapter["标题"]
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"第{chapter_id}章: {chapter_title}")
            
            with col2:
                if str(chapter_id) in st.session_state.chapters:
                    st.success("已生成")
                else:
                    if st.button(f"生成章节", key=f"gen_chapter_{chapter_id}"):
                        with st.spinner(f"正在生成第{chapter_id}章..."):
                            try:
                                payload = {
                                    "chapter_id": chapter_id,
                                    "request_id": st.session_state.request_id
                                }
                                response = requests.post(f"{API_BASE_URL}/generate-chapter", json=payload)
                                if response.status_code == 200:
                                    data = response.json()
                                    st.session_state.chapters[str(chapter_id)] = {
                                        "title": chapter_title,
                                        "content": data["chapter_content"]
                                    }
                                    st.success(f"第{chapter_id}章生成成功！")
                                    st.experimental_rerun()
                                else:
                                    st.error(f"生成章节失败: {response.text}")
                            except Exception as e:
                                st.error(f"发生错误: {str(e)}")
            
            with col3:
                if str(chapter_id) in st.session_state.chapters:
                    if st.button(f"查看章节", key=f"view_chapter_{chapter_id}"):
                        st.session_state.current_chapter = chapter_id
                        st.session_state.step = "view_chapter"
                        st.experimental_rerun()
        
        # 导出小说按钮
        if len(st.session_state.chapters) > 0:
            st.markdown("---")
            if st.button("导出完整小说"):
                with st.spinner("正在导出小说..."):
                    try:
                        response = requests.get(f"{API_BASE_URL}/projects/{st.session_state.request_id}/export")
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.exported_novel = data
                            st.session_state.step = "export_novel"
                            st.success("小说导出成功！")
                            st.experimental_rerun()
                        else:
                            st.error(f"导出小说失败: {response.text}")
                    except Exception as e:
                        st.error(f"发生错误: {str(e)}")
    else:
        st.error("无法获取大纲信息")

elif st.session_state.step == "view_chapter":
    # 查看章节
    chapter_id = st.session_state.current_chapter
    chapter = st.session_state.chapters[str(chapter_id)]
    
    st.header(f"第{chapter_id}章: {chapter['title']}")
    
    # 显示章节内容
    st.markdown(chapter["content"])
    
    # 评估和润色按钮
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("评估章节"):
            with st.spinner("正在评估章节..."):
                try:
                    payload = {
                        "chapter_id": chapter_id,
                        "request_id": st.session_state.request_id
                    }
                    response = requests.post(f"{API_BASE_URL}/evaluate-chapter", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.evaluation_result = data
                        st.session_state.step = "view_evaluation"
                        st.success("章节评估完成！")
                        st.experimental_rerun()
                    else:
                        st.error(f"评估章节失败: {response.text}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
    
    with col2:
        if st.button("润色章节"):
            with st.spinner("正在润色章节..."):
                try:
                    payload = {
                        "chapter_id": chapter_id,
                        "request_id": st.session_state.request_id
                    }
                    response = requests.post(f"{API_BASE_URL}/polish-chapter", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.chapters[str(chapter_id)]["content"] = data["polished_content"]
                        st.session_state.polish_result = data["changes_summary"]
                        st.success("章节润色完成！")
                        st.experimental_rerun()
                    else:
                        st.error(f"润色章节失败: {response.text}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
    
    with col3:
        if st.button("生成剧情分支"):
            with st.spinner("正在生成剧情分支..."):
                try:
                    payload = {
                        "chapter_id": chapter_id,
                        "request_id": st.session_state.request_id
                    }
                    response = requests.post(f"{API_BASE_URL}/generate-branches", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.plot_branches = data["plot_branches"]
                        st.session_state.step = "view_branches"
                        st.success("剧情分支生成完成！")
                        st.experimental_rerun()
                    else:
                        st.error(f"生成剧情分支失败: {response.text}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
    
    # 返回按钮
    if st.button("返回章节列表"):
        st.session_state.step = "generate_chapters"
        st.experimental_rerun()

elif st.session_state.step == "view_evaluation":
    # 查看评估结果
    st.header("章节评估结果")
    
    evaluation = st.session_state.evaluation_result
    
    # 显示总分
    st.subheader(f"总评分: {evaluation.get('total_score', 0)}/100")
    
    # 显示各维度评分
    if "dimension_scores" in evaluation:
        st.subheader("各维度评分")
        scores = evaluation["dimension_scores"]
        for dimension, score in scores.items():
            st.markdown(f"**{dimension}**: {score}")
    
    # 显示审核报告
    if "audit_report" in evaluation:
        st.subheader("审核报告")
        report = evaluation["audit_report"]
        
        st.markdown(f"**总体评价**: {report.get('总体评价', '')}")
        
        if "具体问题点" in report:
            st.markdown("**具体问题点**:")
            for problem in report["具体问题点"]:
                st.markdown(f"- {problem}")
        
        if "改进建议" in report:
            st.markdown("**改进建议**:")
            for suggestion in report["改进建议"]:
                st.markdown(f"- {suggestion}")
    
    # 返回按钮
    if st.button("返回章节"):
        st.session_state.step = "view_chapter"
        st.experimental_rerun()

elif st.session_state.step == "view_branches":
    # 查看剧情分支
    st.header("剧情分支选项")
    
    branches = st.session_state.plot_branches
    chapter_id = st.session_state.current_chapter
    
    for i, branch in enumerate(branches):
        with st.expander(f"分支 {i+1}: {branch.get('title', f'分支选项 {i+1}')}", expanded=True):
            st.markdown(f"**描述**: {branch.get('description', '')}")
            st.markdown(f"**后果**: {branch.get('consequences', '')}")
            st.markdown(f"**情感基调**: {branch.get('emotional_tone', '')}")
            
            if st.button(f"选择此分支", key=f"branch_{i}"):
                with st.spinner("正在处理您的选择..."):
                    try:
                        payload = {
                            "branch_id": i,
                            "chapter_id": chapter_id,
                            "request_id": st.session_state.request_id
                        }
                        response = requests.post(f"{API_BASE_URL}/select-branch", json=payload)
                        if response.status_code == 200:
                            st.success("分支选择成功！")
                            st.session_state.step = "view_chapter"
                            st.experimental_rerun()
                        else:
                            st.error(f"选择分支失败: {response.text}")
                    except Exception as e:
                        st.error(f"发生错误: {str(e)}")
    
    # 返回按钮
    if st.button("返回章节"):
        st.session_state.step = "view_chapter"
        st.experimental_rerun()

elif st.session_state.step == "export_novel":
    # 导出小说
    st.header("导出小说")
    
    novel = st.session_state.exported_novel
    
    # 显示小说标题
    st.title(novel.get("title", "自动生成的小说"))
    
    # 导出选项
    export_format = st.selectbox("导出格式", ["Markdown", "纯文本", "HTML"])
    
    if st.button("下载小说"):
        # 构建小说内容
        content = f"# {novel.get('title', '自动生成的小说')}\n\n"
        
        # 添加概述
        content += "## 小说概述\n\n"
        content += novel.get("expanded_concept", "") + "\n\n"
        
        # 添加章节
        for chapter in novel.get("chapters", []):
            content += f"## 第{chapter['chapter_number']}章: {chapter['title']}\n\n"
            content += chapter["content"] + "\n\n"
        
        # 根据选择的格式处理内容
        if export_format == "Markdown":
            # 已经是Markdown格式
            file_content = content
            mime_type = "text/markdown"
            file_ext = "md"
        elif export_format == "纯文本":
            # 移除Markdown标记
            file_content = content.replace("#", "").replace("*", "")
            mime_type = "text/plain"
            file_ext = "txt"
        else:  # HTML
            # 简单转换为HTML
            import markdown
            file_content = markdown.markdown(content)
            mime_type = "text/html"
            file_ext = "html"
        
        # 提供下载链接
        st.download_button(
            label="下载文件",
            data=file_content,
            file_name=f"novel.{file_ext}",
            mime=mime_type
        )
    
    # 返回按钮
    if st.button("返回章节列表"):
        st.session_state.step = "generate_chapters"
        st.experimental_rerun()

# 页脚
st.markdown("---")
st.markdown("© 2025 自动小说生成器 | 基于多智能体协作的全自动多轮交互式小说生成器")
