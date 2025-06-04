"""
小说生成服务层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models import Project, Concept, WorldSetting, PlotOutline, Character, Chapter
from app.db.repositories import (
    ProjectRepository, ConceptRepository, WorldSettingRepository,
    PlotOutlineRepository, CharacterRepository, ChapterRepository
)
from app.agents import (
    NarrativePathfinderAgent,
    WorldWeaverAgent,
    PlotArchitectAgent,
    CharacterSculptorAgent,
    ChapterChroniclerAgent
)
from app.core.llm import OpenAILLM
from app.core.knowledge_base import KnowledgeBase

class NovelGenerationService:
    """小说生成服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.concept_repo = ConceptRepository(db)
        self.world_setting_repo = WorldSettingRepository(db)
        self.plot_outline_repo = PlotOutlineRepository(db)
        self.character_repo = CharacterRepository(db)
        self.chapter_repo = ChapterRepository(db)
        
        # 初始化LLM和知识库
        self.llm = OpenAILLM()
    
    async def generate_concepts(self, project_id: str, user_input: str, num_concepts: int = 3) -> List[Concept]:
        """生成小说概述"""
        # 创建概述智能体
        agent = NarrativePathfinderAgent(llm=self.llm, project_id=project_id)
        
        # 调用智能体生成概述
        result = await agent.run({
            "user_input": user_input,
            "num_concepts": num_concepts,
            "mode": "generate"
        })
        
        # 保存生成的概述到数据库
        concepts = []
        for i, concept_content in enumerate(result["concepts"]):
            concept = self.concept_repo.create(
                project_id=project_id,
                title=f"概述 {i+1}",
                content=concept_content,
                order_index=i
            )
            concepts.append(concept)
        
        return concepts
    
    async def expand_concept(self, concept_id: str) -> Concept:
        """扩展概述为详细情节梗概"""
        concept = self.concept_repo.get_by_id(concept_id)
        if not concept:
            raise ValueError("概述不存在")
        
        # 创建概述智能体
        agent = NarrativePathfinderAgent(llm=self.llm, project_id=concept.project_id)
        
        # 调用智能体扩展概述
        result = await agent.run({
            "selected_concept": concept.content,
            "mode": "expand"
        })
        
        # 更新概述的扩展内容
        updated_concept = self.concept_repo.update(
            concept_id,
            expanded_content=result["expanded_concept"]
        )
        
        return updated_concept
    
    async def generate_world_settings(self, project_id: str, num_settings: int = 2) -> List[WorldSetting]:
        """生成世界观设定"""
        print(f"服务层：开始生成世界观设定，项目ID: {project_id}")

        try:
            # 获取选中的概述
            selected_concept = self.concept_repo.get_selected_by_project_id(project_id)
            if not selected_concept:
                print(f"服务层：未找到选中的概述，项目ID: {project_id}")
                raise ValueError("请先选择一个概述")

            print(f"服务层：找到选中的概述，ID: {selected_concept.id}")

            # 创建世界观智能体
            agent = WorldWeaverAgent(llm=self.llm, project_id=project_id)

            # 调用智能体生成世界观设定
            narrative_content = selected_concept.expanded_content or selected_concept.content
            print(f"服务层：使用概述内容长度: {len(narrative_content)}")

            if not narrative_content.strip():
                raise ValueError("概述内容为空，无法生成世界观设定")

            result = await agent.run({
                "narrative_concept": narrative_content,
                "num_settings": num_settings
            })

            if not result or "world_settings" not in result:
                raise ValueError("智能体未返回有效的世界观设定")

            print(f"服务层：智能体返回 {len(result.get('world_settings', []))} 个世界观设定")

            # 保存生成的世界观设定到数据库
            world_settings = []
            for i, setting_content in enumerate(result["world_settings"]):
                print(f"服务层：保存第 {i+1} 个世界观设定")
                try:
                    world_setting = self.world_setting_repo.create(
                        project_id=project_id,
                        title=f"世界观设定 {i+1}",
                        content=setting_content,
                        order_index=i
                    )
                    world_settings.append(world_setting)
                except Exception as e:
                    print(f"服务层：保存第 {i+1} 个世界观设定失败: {str(e)}")
                    raise ValueError(f"保存世界观设定失败: {str(e)}")

            print(f"服务层：成功保存 {len(world_settings)} 个世界观设定")
            return world_settings

        except ValueError:
            # 重新抛出业务逻辑错误
            raise
        except Exception as e:
            print(f"服务层：生成世界观设定时发生未知错误: {str(e)}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"生成世界观设定时发生错误: {str(e)}")
    
    async def generate_plot_outlines(self, project_id: str, chapter_count: int = 10, 
                                   conflict_elements: str = "") -> List[PlotOutline]:
        """生成大纲"""
        # 获取选中的概述和世界观设定
        selected_concept = self.concept_repo.get_selected_by_project_id(project_id)
        selected_world_setting = self.world_setting_repo.get_selected_by_project_id(project_id)
        
        if not selected_concept or not selected_world_setting:
            raise ValueError("请先选择概述和世界观设定")
        
        # 创建大纲智能体
        agent = PlotArchitectAgent(llm=self.llm, project_id=project_id)
        
        # 调用智能体生成大纲
        result = await agent.run({
            "narrative_concept": selected_concept.expanded_content or selected_concept.content,
            "world_setting": selected_world_setting.content,
            "chapter_count": chapter_count,
            "conflict_elements": conflict_elements
        })
        
        # 保存生成的大纲到数据库
        plot_outlines = []
        for i, outline_content in enumerate(result["plot_outlines"]):
            # 如果outline_content是字符串，尝试解析为结构化数据
            if isinstance(outline_content, str):
                print(f"处理字符串格式的大纲内容: {outline_content[:200]}...")
                # 简单的结构化处理
                structured_outline = {
                    "raw_content": outline_content,
                    "structure": "基于选定概述和世界观的详细大纲",
                    "chapters": [],
                    "chapter_details": []
                }

                # 尝试提取章节信息
                lines = outline_content.split('\n')
                chapter_number = 1
                for line in lines:
                    line = line.strip()
                    if (line.startswith('第') and '章' in line) or (line.startswith('Chapter') and ':' in line):
                        # 提取章节标题
                        if '第' in line and '章' in line:
                            title_part = line.split('章', 1)
                            if len(title_part) > 1:
                                title = title_part[1].replace(':', '').strip()
                            else:
                                title = f"章节 {chapter_number}"
                        else:
                            title = line.split(':', 1)[1].strip() if ':' in line else f"章节 {chapter_number}"

                        structured_outline["chapters"].append({
                            "number": chapter_number,
                            "title": title,
                            "word_count": "3000-5000"
                        })
                        structured_outline["chapter_details"].append({
                            "number": chapter_number,
                            "title": title,
                            "scenes": "主要场景将在此展开",
                            "characters": "主要人物登场",
                            "events": "核心情节发展",
                            "conflicts": "主要冲突点",
                            "turning_points": "关键转折时刻",
                            "emotional_tone": "情感氛围营造",
                            "foreshadowing": "伏笔和悬念设置"
                        })
                        chapter_number += 1

                # 如果没有找到章节，创建默认章节
                if not structured_outline["chapters"]:
                    for j in range(chapter_count):
                        chapter_num = j + 1
                        structured_outline["chapters"].append({
                            "number": chapter_num,
                            "title": f"第{chapter_num}章",
                            "word_count": "3000-5000"
                        })
                        structured_outline["chapter_details"].append({
                            "number": chapter_num,
                            "title": f"第{chapter_num}章",
                            "scenes": "场景描述",
                            "characters": "人物设定",
                            "events": "事件发展",
                            "conflicts": "冲突设置",
                            "turning_points": "转折点",
                            "emotional_tone": "情感基调",
                            "foreshadowing": "伏笔悬念"
                        })

                outline_data = structured_outline
            else:
                outline_data = outline_content

            plot_outline = self.plot_outline_repo.create(
                project_id=project_id,
                title=f"大纲 {i+1}",
                content=outline_data,
                order_index=i
            )
            plot_outlines.append(plot_outline)

        return plot_outlines
    
    async def generate_characters(self, project_id: str, num_character_sets: int = 1) -> List[Character]:
        """生成人物设定"""
        # 获取选中的概述、世界观设定和大纲
        selected_concept = self.concept_repo.get_selected_by_project_id(project_id)
        selected_world_setting = self.world_setting_repo.get_selected_by_project_id(project_id)
        selected_plot_outline = self.plot_outline_repo.get_selected_by_project_id(project_id)
        
        if not all([selected_concept, selected_world_setting, selected_plot_outline]):
            raise ValueError("请先选择概述、世界观设定和大纲")
        
        # 创建人物刻画智能体
        agent = CharacterSculptorAgent(llm=self.llm, project_id=project_id)
        
        # 调用智能体生成人物设定
        result = await agent.run({
            "narrative_concept": selected_concept.expanded_content or selected_concept.content,
            "world_setting": selected_world_setting.content,
            "plot_outline": selected_plot_outline.content,
            "num_character_sets": num_character_sets
        })
        
        # 保存生成的人物设定到数据库
        characters = []
        character_profiles = result.get("character_profiles", [])

        print(f"获取到的人物设定数据: {character_profiles}")

        for i, character_profile in enumerate(character_profiles):
            # 处理不同格式的人物设定数据
            if isinstance(character_profile, str):
                # 如果是字符串，创建简单的结构化数据
                character_data = {
                    "set_number": i + 1,
                    "description": character_profile,
                    "characters": [
                        {
                            "name": f"主角{i+1}",
                            "age": "待定",
                            "background": character_profile[:200] + "..." if len(character_profile) > 200 else character_profile,
                            "personality": "性格待定",
                            "appearance": "外貌待定",
                            "skills": "技能待定",
                            "relationships": "关系待定",
                            "arc": "发展弧线待定"
                        }
                    ]
                }
            elif isinstance(character_profile, dict):
                # 如果是字典，检查是否有raw_text字段
                if "raw_text" in character_profile:
                    character_data = {
                        "set_number": i + 1,
                        "description": character_profile["raw_text"],
                        "characters": [
                            {
                                "name": f"主角{i+1}",
                                "age": "待定",
                                "background": character_profile["raw_text"][:200] + "..." if len(character_profile["raw_text"]) > 200 else character_profile["raw_text"],
                                "personality": "性格待定",
                                "appearance": "外貌待定",
                                "skills": "技能待定",
                                "relationships": "关系待定",
                                "arc": "发展弧线待定"
                            }
                        ]
                    }
                else:
                    # 如果是结构化的人物设定数据，直接使用
                    character_data = {
                        "set_number": i + 1,
                        "characters": character_profile.get("人物设定", [character_profile]) if "人物设定" in character_profile else [character_profile],
                        "description": character_profile.get("人物关系图谱", "人物设定集")
                    }
            else:
                # 其他情况，创建默认数据
                character_data = {
                    "set_number": i + 1,
                    "description": f"人物设定集 {i+1}",
                    "characters": [
                        {
                            "name": f"主角{i+1}",
                            "age": "待定",
                            "background": "角色背景",
                            "personality": "性格特点",
                            "appearance": "外貌描述",
                            "skills": "技能特长",
                            "relationships": "人物关系",
                            "arc": "角色弧光"
                        }
                    ]
                }

            character = self.character_repo.create(
                project_id=project_id,
                name=f"人物设定集 {i+1}",
                content=character_data,
                order_index=i,
                character_type="character_set"
            )
            characters.append(character)

        return characters
    
    async def generate_chapter(self, project_id: str, chapter_number: int, 
                             writing_style: str = "详细生动") -> Chapter:
        """生成章节内容"""
        # 获取必要的数据
        selected_concept = self.concept_repo.get_selected_by_project_id(project_id)
        selected_world_setting = self.world_setting_repo.get_selected_by_project_id(project_id)
        selected_plot_outline = self.plot_outline_repo.get_selected_by_project_id(project_id)
        selected_characters = self.character_repo.get_selected_by_project_id(project_id)
        
        if not all([selected_concept, selected_world_setting, selected_plot_outline]):
            raise ValueError("请先完成前面的步骤")
        
        # 获取章节大纲
        chapter_outline = self._extract_chapter_outline(selected_plot_outline.content, chapter_number)
        
        # 获取前情提要
        previous_summary = await self._get_previous_summary(project_id, chapter_number)
        
        # 创建章节智能体
        agent = ChapterChroniclerAgent(llm=self.llm, project_id=project_id)
        
        # 调用智能体生成章节内容
        result = await agent.run({
            "chapter_outline": chapter_outline,
            "world_setting": selected_world_setting.content,
            "character_profiles": [char.content for char in selected_characters],
            "previous_summary": previous_summary,
            "writing_style": writing_style,
            "mode": "generate"
        })
        
        # 保存章节到数据库
        chapter = self.chapter_repo.create(
            project_id=project_id,
            chapter_number=chapter_number,
            title=chapter_outline.get("title", f"第{chapter_number}章"),
            content=result["chapter_content"],
            outline=chapter_outline,
            writing_style=writing_style,
            word_count=len(result["chapter_content"])
        )
        
        return chapter
    
    def _extract_chapter_outline(self, plot_outline: Dict[str, Any], chapter_number: int) -> Dict[str, Any]:
        """从大纲中提取指定章节的大纲"""
        # 尝试多种可能的结构
        possible_keys = ["章节列表", "chapters", "chapter_details", "章节详情"]

        for key in possible_keys:
            if key in plot_outline:
                chapters = plot_outline[key]
                if isinstance(chapters, list):
                    for chapter in chapters:
                        if isinstance(chapter, dict):
                            # 尝试多种可能的章节号字段
                            chapter_num_keys = ["章节号", "number", "chapter_number", "num"]
                            for num_key in chapter_num_keys:
                                if chapter.get(num_key) == chapter_number:
                                    return chapter

        # 如果没有找到，创建默认章节大纲
        return {
            "number": chapter_number,
            "title": f"第{chapter_number}章",
            "scenes": "主要场景描述",
            "events": "核心事件发展",
            "conflicts": "主要冲突点",
            "turning_points": "关键转折",
            "emotional_tone": "情感基调",
            "foreshadowing": "伏笔悬念",
            "characters": "主要人物",
            "word_count": "3000-5000"
        }
    
    async def _get_previous_summary(self, project_id: str, chapter_number: int) -> str:
        """获取前情提要"""
        if chapter_number <= 1:
            return ""

        # 获取前面的章节
        previous_chapters = self.chapter_repo.get_by_project_id(project_id)
        previous_chapters = [ch for ch in previous_chapters if ch.chapter_number < chapter_number]

        if not previous_chapters:
            return ""

        # 生成详细的前情提要
        summary_parts = []

        # 获取项目的基本信息
        selected_concept = self.concept_repo.get_selected_by_project_id(project_id)
        selected_world_setting = self.world_setting_repo.get_selected_by_project_id(project_id)
        selected_characters = self.character_repo.get_selected_by_project_id(project_id)

        # 添加基本设定信息
        if selected_concept:
            summary_parts.append(f"故事背景：{selected_concept.content[:200]}...")

        if selected_world_setting:
            world_content = selected_world_setting.content
            if isinstance(world_content, dict):
                world_desc = world_content.get("description", "")
                if world_desc:
                    summary_parts.append(f"世界观：{world_desc[:200]}...")

        if selected_characters:
            char_content = selected_characters[0].content if selected_characters else {}
            if isinstance(char_content, dict) and "characters" in char_content:
                char_names = [char.get("name", "") for char in char_content["characters"][:3]]
                if char_names:
                    summary_parts.append(f"主要人物：{', '.join(char_names)}")

        # 添加前面章节的摘要
        summary_parts.append("\n前情回顾：")
        for chapter in previous_chapters[-3:]:  # 只取最近3章
            content_preview = chapter.content[:300] if chapter.content else ""
            summary_parts.append(f"第{chapter.chapter_number}章《{chapter.title}》：{content_preview}...")

        return "\n".join(summary_parts)
