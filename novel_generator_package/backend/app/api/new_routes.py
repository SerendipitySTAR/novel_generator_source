"""
新的API路由定义，使用数据库和服务层
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services import ProjectService, NovelGenerationService
from app.models import Project, Concept, WorldSetting, PlotOutline, Character, Chapter

# 创建路由器
router = APIRouter(tags=["novel-generator"])

# 健康检查路由
@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db_gen = get_db()
        db = next(db_gen)
        try:
            # 简单的数据库查询测试
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"error: {str(e)}"
        finally:
            db.close()

        return {
            "status": "healthy",
            "database": db_status,
            "message": "小说生成器API服务正常运行"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"服务异常: {str(e)}"
        }

# 请求模型
class ProjectCreateRequest(BaseModel):
    title: str
    description: str = ""
    target_chapters: int = 10
    writing_style: str = "详细生动"
    genre: str = ""

class ConceptGenerateRequest(BaseModel):
    user_input: str
    num_concepts: int = 3

class ConceptSelectRequest(BaseModel):
    concept_id: str

class WorldSettingGenerateRequest(BaseModel):
    num_settings: int = 2

class PlotOutlineGenerateRequest(BaseModel):
    chapter_count: int = 10
    conflict_elements: str = ""

class CharacterGenerateRequest(BaseModel):
    num_character_sets: int = 1

class ChapterGenerateRequest(BaseModel):
    chapter_number: int
    writing_style: str = "详细生动"

class ChapterGenerateRequestV2(BaseModel):
    chapter_outline: dict # Should include chapter_number, title, etc.
    world_setting: dict
    character_profiles: list # List of character profile dicts
    previous_summary: str = ""
    kb_context: list = []
    writing_style: str = "详细生动"

class ChapterGenerateRequestV3(ChapterGenerateRequestV2):
    novel_progress: Optional[float] = None  # e.g., 0.0 (start) to 1.0 (end)
    tension_level: Optional[str] = None     # e.g., "low", "rising", "peak", "falling", "resolution"
    chapter_type: Optional[str] = None      # e.g., "introduction", "rising_action", "climax", "subplot_development"
    long_term_goals: Optional[List[str]] = None # List of active long-term plot points or character arcs for this chapter

class ChapterGenerateWithQualityCheckRequest(BaseModel):
    chapter_outline: dict
    world_setting: dict
    character_profiles: list
    previous_summary: str = ""
    previous_chapters: list = []
    kb_context: list = []
    writing_style: str = "详细生动"
    max_retries: int = 2

# 响应模型
class ProjectResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    created_at: str
    updated_at: str

class ConceptResponse(BaseModel):
    id: str
    title: str
    content: str
    expanded_content: Optional[str]
    is_selected: bool

# 依赖注入
def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """获取项目服务实例"""
    return ProjectService(db)

def get_novel_service(db: Session = Depends(get_db)) -> NovelGenerationService:
    """获取小说生成服务实例"""
    return NovelGenerationService(db)

# 项目管理路由
@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    request: ProjectCreateRequest,
    project_service: ProjectService = Depends(get_project_service)
):
    """创建新项目"""
    project = project_service.create_project(
        title=request.title,
        description=request.description,
        target_chapters=request.target_chapters,
        writing_style=request.writing_style,
        genre=request.genre
    )
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        created_at=project.created_at if isinstance(project.created_at, str) else project.created_at.isoformat(),
        updated_at=project.updated_at if isinstance(project.updated_at, str) else (project.updated_at.isoformat() if project.updated_at else project.created_at)
    )

@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    project_service: ProjectService = Depends(get_project_service)
):
    """获取项目列表"""
    projects = project_service.get_all_projects(skip=skip, limit=limit)
    return [
        ProjectResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            status=project.status,
            created_at=project.created_at if isinstance(project.created_at, str) else project.created_at.isoformat(),
            updated_at=project.updated_at if isinstance(project.updated_at, str) else (project.updated_at.isoformat() if project.updated_at else project.created_at)
        )
        for project in projects
    ]

@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """获取项目详情"""
    summary = project_service.get_project_summary(project_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Project not found")
    return summary

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """删除项目"""
    success = project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# 概述生成路由
@router.post("/projects/{project_id}/concepts")
async def generate_concepts(
    project_id: str,
    request: ConceptGenerateRequest,
    novel_service: NovelGenerationService = Depends(get_novel_service),
    project_service: ProjectService = Depends(get_project_service)
):
    """生成小说概述"""
    # 检查项目是否存在
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        concepts = await novel_service.generate_concepts(
            project_id=project_id,
            user_input=request.user_input,
            num_concepts=request.num_concepts
        )
        
        return {
            "concepts": [
                ConceptResponse(
                    id=concept.id,
                    title=concept.title,
                    content=concept.content,
                    expanded_content=concept.expanded_content,
                    is_selected=concept.is_selected
                )
                for concept in concepts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}/concepts")
async def get_concepts(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取项目的概述列表"""
    from app.db.repositories import ConceptRepository
    concept_repo = ConceptRepository(db)
    concepts = concept_repo.get_by_project_id(project_id)
    
    return {
        "concepts": [
            ConceptResponse(
                id=concept.id,
                title=concept.title,
                content=concept.content,
                expanded_content=concept.expanded_content,
                is_selected=concept.is_selected
            )
            for concept in concepts
        ]
    }

@router.post("/projects/{project_id}/concepts/{concept_id}/select")
async def select_concept(
    project_id: str,
    concept_id: str,
    db: Session = Depends(get_db)
):
    """选择概述"""
    from app.db.repositories import ConceptRepository
    concept_repo = ConceptRepository(db)

    success = concept_repo.set_selected(project_id, concept_id)
    if not success:
        raise HTTPException(status_code=404, detail="Concept not found")

    # 返回更新后的概述
    concept = concept_repo.get_by_id(concept_id)
    if concept:
        return ConceptResponse(
            id=concept.id,
            title=concept.title,
            content=concept.content,
            expanded_content=concept.expanded_content,
            is_selected=concept.is_selected
        )

    return {"message": "Concept selected successfully"}

@router.post("/projects/{project_id}/concepts/{concept_id}/expand")
async def expand_concept(
    project_id: str,
    concept_id: str,
    novel_service: NovelGenerationService = Depends(get_novel_service)
):
    """扩展概述"""
    try:
        concept = await novel_service.expand_concept(concept_id)
        return ConceptResponse(
            id=concept.id,
            title=concept.title,
            content=concept.content,
            expanded_content=concept.expanded_content,
            is_selected=concept.is_selected
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 世界观设定路由
@router.post("/projects/{project_id}/world-settings")
async def generate_world_settings(
    project_id: str,
    request: WorldSettingGenerateRequest,
    novel_service: NovelGenerationService = Depends(get_novel_service)
):
    """生成世界观设定"""
    try:
        print(f"开始生成世界观设定，项目ID: {project_id}, 数量: {request.num_settings}")

        # 验证项目是否存在
        from app.db.repositories import ProjectRepository

        db_gen = get_db()
        db = next(db_gen)
        try:
            project_repo = ProjectRepository(db)
            project = project_repo.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
        finally:
            db.close()

        world_settings = await novel_service.generate_world_settings(
            project_id=project_id,
            num_settings=request.num_settings
        )

        print(f"成功生成 {len(world_settings)} 个世界观设定")

        return {
            "world_settings": [
                {
                    "id": ws.id,
                    "title": ws.title,
                    "content": ws.content,
                    "is_selected": ws.is_selected
                }
                for ws in world_settings
            ]
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except ValueError as e:
        print(f"世界观生成失败 - 参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"世界观生成失败 - 系统错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成世界观设定时发生错误: {str(e)}")

@router.get("/projects/{project_id}/world-settings")
async def get_world_settings(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取项目的世界观设定列表"""
    try:
        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, WorldSettingRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        world_setting_repo = WorldSettingRepository(db)
        world_settings = world_setting_repo.get_by_project_id(project_id)

        return {
            "world_settings": [
                {
                    "id": ws.id,
                    "title": ws.title,
                    "content": ws.content,
                    "is_selected": ws.is_selected
                }
                for ws in world_settings
            ]
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"获取世界观设定失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取世界观设定时发生错误: {str(e)}")

@router.put("/projects/{project_id}/world-settings/{world_setting_id}")
async def update_world_setting(
    project_id: str,
    world_setting_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """更新世界观设定"""
    try:
        from app.db.repositories import WorldSettingRepository
        world_setting_repo = WorldSettingRepository(db)

        # 获取世界观设定
        world_setting = world_setting_repo.get_by_id(world_setting_id)
        if not world_setting or world_setting.project_id != project_id:
            raise HTTPException(status_code=404, detail="世界观设定不存在")

        # 如果要设置为选中状态，先取消其他选中状态
        if update_data.get("is_selected", False):
            success = world_setting_repo.set_selected(project_id, world_setting_id)
            if not success:
                raise HTTPException(status_code=400, detail="设置选中状态失败")

        return {
            "id": world_setting.id,
            "title": world_setting.title,
            "content": world_setting.content,
            "is_selected": world_setting.is_selected
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"更新世界观设定失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"更新世界观设定时发生错误: {str(e)}")

@router.post("/projects/{project_id}/world-settings/{world_setting_id}/select")
async def select_world_setting(
    project_id: str,
    world_setting_id: str,
    db: Session = Depends(get_db)
):
    """选择世界观设定"""
    from app.db.repositories import WorldSettingRepository
    world_setting_repo = WorldSettingRepository(db)

    success = world_setting_repo.set_selected(project_id, world_setting_id)
    if not success:
        raise HTTPException(status_code=404, detail="World setting not found")

    # 返回更新后的世界观设定
    world_setting = world_setting_repo.get_by_id(world_setting_id)
    if world_setting:
        return {
            "id": world_setting.id,
            "title": world_setting.title,
            "content": world_setting.content,
            "is_selected": world_setting.is_selected
        }

    return {"message": "World setting selected successfully"}

# 大纲生成路由
@router.post("/projects/{project_id}/plot-outlines")
async def generate_plot_outlines(
    project_id: str,
    request: PlotOutlineGenerateRequest,
    novel_service: NovelGenerationService = Depends(get_novel_service)
):
    """生成大纲"""
    try:
        print(f"开始生成大纲，项目ID: {project_id}")

        # 验证项目是否存在
        from app.db.repositories import ProjectRepository

        db_gen = get_db()
        db = next(db_gen)
        try:
            project_repo = ProjectRepository(db)
            project = project_repo.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
        finally:
            db.close()

        plot_outlines = await novel_service.generate_plot_outlines(
            project_id=project_id,
            chapter_count=request.chapter_count,
            conflict_elements=request.conflict_elements
        )

        print(f"成功生成 {len(plot_outlines)} 个大纲")

        return {
            "plot_outlines": [
                {
                    "id": po.id,
                    "title": po.title,
                    "content": po.content,
                    "is_selected": po.is_selected
                }
                for po in plot_outlines
            ]
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except ValueError as e:
        print(f"大纲生成失败 - 参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"大纲生成失败 - 系统错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成大纲时发生错误: {str(e)}")

@router.get("/projects/{project_id}/plot-outlines")
async def get_plot_outlines(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取项目的大纲列表"""
    try:
        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, PlotOutlineRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        plot_outline_repo = PlotOutlineRepository(db)
        plot_outlines = plot_outline_repo.get_by_project_id(project_id)

        return {
            "plot_outlines": [
                {
                    "id": po.id,
                    "title": po.title,
                    "content": po.content,
                    "is_selected": po.is_selected
                }
                for po in plot_outlines
            ]
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"获取大纲失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取大纲时发生错误: {str(e)}")

@router.put("/projects/{project_id}/plot-outlines/{plot_outline_id}")
async def update_plot_outline(
    project_id: str,
    plot_outline_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """更新大纲"""
    try:
        from app.db.repositories import PlotOutlineRepository
        plot_outline_repo = PlotOutlineRepository(db)

        # 获取大纲
        plot_outline = plot_outline_repo.get_by_id(plot_outline_id)
        if not plot_outline or plot_outline.project_id != project_id:
            raise HTTPException(status_code=404, detail="大纲不存在")

        # 如果要设置为选中状态，先取消其他选中状态
        if update_data.get("is_selected", False):
            success = plot_outline_repo.set_selected(project_id, plot_outline_id)
            if not success:
                raise HTTPException(status_code=400, detail="设置选中状态失败")

        # 更新其他字段
        update_fields = {}
        if "content" in update_data:
            update_fields["content"] = update_data["content"]
        if "title" in update_data:
            update_fields["title"] = update_data["title"]

        if update_fields:
            updated_plot_outline = plot_outline_repo.update(plot_outline_id, **update_fields)
            plot_outline = updated_plot_outline

        return {
            "id": plot_outline.id,
            "title": plot_outline.title,
            "content": plot_outline.content,
            "is_selected": plot_outline.is_selected
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"更新大纲失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"更新大纲时发生错误: {str(e)}")

@router.post("/projects/{project_id}/plot-outlines/{plot_outline_id}/select")
async def select_plot_outline(
    project_id: str,
    plot_outline_id: str,
    db: Session = Depends(get_db)
):
    """选择大纲"""
    from app.db.repositories import PlotOutlineRepository
    plot_outline_repo = PlotOutlineRepository(db)

    success = plot_outline_repo.set_selected(project_id, plot_outline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plot outline not found")

    # 返回更新后的大纲
    plot_outline = plot_outline_repo.get_by_id(plot_outline_id)
    if plot_outline:
        return {
            "id": plot_outline.id,
            "title": plot_outline.title,
            "content": plot_outline.content,
            "is_selected": plot_outline.is_selected
        }

    return {"message": "Plot outline selected successfully"}

# 人物设定路由
@router.post("/projects/{project_id}/characters")
async def generate_characters(
    project_id: str,
    request: CharacterGenerateRequest,
    novel_service: NovelGenerationService = Depends(get_novel_service)
):
    """生成人物设定"""
    try:
        print(f"开始生成人物设定，项目ID: {project_id}")

        # 验证项目是否存在
        from app.db.repositories import ProjectRepository

        db_gen = get_db()
        db = next(db_gen)
        try:
            project_repo = ProjectRepository(db)
            project = project_repo.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
        finally:
            db.close()

        characters = await novel_service.generate_characters(
            project_id=project_id,
            num_character_sets=request.num_character_sets
        )

        print(f"成功生成 {len(characters)} 个人物设定")

        return {
            "characters": [
                {
                    "id": char.id,
                    "name": char.name,
                    "content": char.content,
                    "is_selected": char.is_selected,
                    "character_type": char.character_type
                }
                for char in characters
            ]
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except ValueError as e:
        print(f"人物设定生成失败 - 参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"人物设定生成失败 - 系统错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成人物设定时发生错误: {str(e)}")

@router.get("/projects/{project_id}/characters")
async def get_characters(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取项目的人物设定列表"""
    try:
        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, CharacterRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        character_repo = CharacterRepository(db)
        characters = character_repo.get_by_project_id(project_id)

        return {
            "characters": [
                {
                    "id": char.id,
                    "name": char.name,
                    "content": char.content,
                    "is_selected": char.is_selected,
                    "character_type": char.character_type
                }
                for char in characters
            ]
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"获取人物设定失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取人物设定时发生错误: {str(e)}")

@router.put("/projects/{project_id}/characters/{character_id}")
async def update_character(
    project_id: str,
    character_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """更新人物设定"""
    try:
        from app.db.repositories import CharacterRepository
        character_repo = CharacterRepository(db)

        # 获取人物设定
        character = character_repo.get_by_id(character_id)
        if not character or character.project_id != project_id:
            raise HTTPException(status_code=404, detail="人物设定不存在")

        # 如果要设置为选中状态，先取消其他选中状态
        if update_data.get("is_selected", False):
            success = character_repo.set_selected(project_id, character_id)
            if not success:
                raise HTTPException(status_code=400, detail="设置选中状态失败")

        # 更新其他字段
        update_fields = {}
        if "content" in update_data:
            update_fields["content"] = update_data["content"]
        if "name" in update_data:
            update_fields["name"] = update_data["name"]
        if "character_type" in update_data:
            update_fields["character_type"] = update_data["character_type"]

        if update_fields:
            updated_character = character_repo.update(character_id, **update_fields)
            character = updated_character

        return {
            "id": character.id,
            "name": character.name,
            "content": character.content,
            "is_selected": character.is_selected,
            "character_type": character.character_type
        }
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"更新人物设定失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"更新人物设定时发生错误: {str(e)}")

@router.post("/projects/{project_id}/characters/{character_id}/select")
async def select_character(
    project_id: str,
    character_id: str,
    db: Session = Depends(get_db)
):
    """选择人物设定"""
    from app.db.repositories import CharacterRepository
    character_repo = CharacterRepository(db)

    success = character_repo.set_selected(project_id, character_id)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")

    # 返回更新后的人物设定
    character = character_repo.get_by_id(character_id)
    if character:
        return {
            "id": character.id,
            "name": character.name,
            "content": character.content,
            "is_selected": character.is_selected,
            "character_type": character.character_type
        }

    return {"message": "Character selected successfully"}

# 章节路由
@router.get("/projects/{project_id}/chapters")
async def get_chapters(
    project_id: str,
    db: Session = Depends(get_db)
):
    """获取项目的章节列表"""
    try:
        print(f"=== 获取章节列表请求 ===")
        print(f"项目ID: {project_id}")

        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, ChapterRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            print(f"项目不存在: {project_id}")
            raise HTTPException(status_code=404, detail="项目不存在")

        chapter_repo = ChapterRepository(db)
        chapters = chapter_repo.get_by_project_id(project_id)

        print(f"从数据库获取到 {len(chapters)} 个章节")
        for chapter in chapters:
            print(f"章节: {chapter.id}, 章节号: {chapter.chapter_number}, 标题: {chapter.title}")

        result = [
            {
                "id": chapter.id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "content": chapter.content,
                "word_count": chapter.word_count or len(chapter.content or ""),
                "writing_style": chapter.writing_style,
                "status": chapter.status or "draft",
                "created_at": chapter.created_at if isinstance(chapter.created_at, str) else (chapter.created_at.isoformat() if chapter.created_at else None),
                "updated_at": chapter.updated_at if isinstance(chapter.updated_at, str) else (chapter.updated_at.isoformat() if chapter.updated_at else None)
            }
            for chapter in chapters
        ]

        print(f"返回章节数据: {len(result)} 个章节")
        return result
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"获取章节失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取章节时发生错误: {str(e)}")

@router.post("/projects/{project_id}/chapters")
async def generate_chapter(
    project_id: str,
    request: ChapterGenerateRequestV3, # Changed to V3
    novel_service: NovelGenerationService = Depends(get_novel_service) # novel_service is injected but not used directly here for agent call
):
    """生成章节内容"""
    try:
        print(f"=== 章节生成请求开始 (V3) ===")
        print(f"项目ID: {project_id}")
        print(f"请求数据: {request.model_dump()}")
        # Removed detailed logging of each field for brevity, model_dump() covers it.

        # 验证项目是否存在 (This should ideally be handled by the service layer or a dependency)
        from app.db.repositories import ProjectRepository
        db_gen = get_db()
        db = next(db_gen)
        try:
            project_repo = ProjectRepository(db)
            project = project_repo.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
        finally:
            db.close()

        # 使用ChapterChroniclerAgent直接生成章节
        from app.agents.chapter_chronicler import ChapterChroniclerAgent
        from app.core.llm import OpenAILLM # Assuming OpenAILLM is the desired LLM interface

        # It might be better to get the LLM instance from a central place if possible,
        # e.g., from novel_service.llm if it's exposed and appropriate.
        agent = ChapterChroniclerAgent(llm=OpenAILLM(), project_id=project_id)

        # Prepare input_data for the agent, including new fields
        input_data_for_agent = {
            "mode": "generate",
            "chapter_outline": request.chapter_outline,
            "world_setting": request.world_setting,
            "character_profiles": request.character_profiles,
            "previous_summary": request.previous_summary,
            "kb_context": request.kb_context,
            "writing_style": request.writing_style,
            # New fields for V3
            "novel_progress": request.novel_progress,
            "tension_level": request.tension_level,
            "chapter_type": request.chapter_type,
            "long_term_goals": request.long_term_goals,
        }

        # 调用智能体生成章节内容
        result = await agent.run(input_data_for_agent)

        # 添加调试日志
        print(f"智能体返回结果: {result}")
        chapter_content = result.get("chapter_content", "")
        print(f"章节内容长度: {len(chapter_content)}")

        # 确保章节内容不为空
        if not chapter_content or chapter_content.strip() == "":
            chapter_content = "章节内容生成失败，请重试生成。如果问题持续存在，请检查AI服务配置。"
            print("警告: 章节内容为空，使用默认内容")

        # 保存章节到数据库
        from app.db.repositories import ChapterRepository

        db_gen = get_db()
        db = next(db_gen)
        try:
            chapter_repo = ChapterRepository(db)
            chapter = chapter_repo.create(
                project_id=project_id,
                chapter_number=request.chapter_outline.get("number", 1),
                title=request.chapter_outline.get("title", f"第{request.chapter_outline.get('number', 1)}章"),
                content=chapter_content,
                outline=request.chapter_outline,
                writing_style=request.writing_style,
                word_count=len(chapter_content)
            )
        finally:
            db.close()

        print(f"成功生成章节: {chapter.title}")
        print(f"章节ID: {chapter.id}")
        print(f"章节号: {chapter.chapter_number}")
        print(f"内容长度: {len(chapter.content or '')}")

        response_data = {
            "id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "content": chapter.content,
            "word_count": chapter.word_count or len(chapter.content or ""),
            "writing_style": chapter.writing_style,
            "status": chapter.status or "draft",
            "created_at": chapter.created_at if isinstance(chapter.created_at, str) else (chapter.created_at.isoformat() if chapter.created_at else None),
            "updated_at": chapter.updated_at if isinstance(chapter.updated_at, str) else (chapter.updated_at.isoformat() if chapter.updated_at else None)
        }

        print(f"返回响应数据: {response_data}")
        return response_data
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except ValueError as e:
        print(f"章节生成失败 - 参数错误: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"章节生成失败 - 系统错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成章节时发生错误: {str(e)}")

@router.post("/projects/{project_id}/chapters/generate-with-quality-check")
async def generate_chapter_with_quality_check(
    project_id: str,
    request: ChapterGenerateWithQualityCheckRequest,
    novel_service: NovelGenerationService = Depends(get_novel_service)
):
    """生成章节内容（带质量检查和智能重试）"""
    try:
        print(f"=== 带质量检查的章节生成请求开始 ===")
        print(f"项目ID: {project_id}")
        print(f"最大重试次数: {request.max_retries}")

        # 验证项目是否存在
        from app.db.repositories import ProjectRepository

        db_gen = get_db()
        db = next(db_gen)
        try:
            project_repo = ProjectRepository(db)
            project = project_repo.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
        finally:
            db.close()

        # 使用智能体进行多轮生成和质量检查
        from app.agents.chapter_chronicler import ChapterChroniclerAgent
        from app.agents.quality_guardian import QualityGuardianAgent
        from app.core.llm import OpenAILLM

        llm = OpenAILLM()
        chapter_agent = ChapterChroniclerAgent(llm=llm, project_id=project_id)
        quality_agent = QualityGuardianAgent(llm=llm, project_id=project_id)

        best_result = None
        best_score = 0
        generation_attempts = []

        for attempt in range(request.max_retries + 1):
            print(f"第 {attempt + 1} 次生成尝试")

            # 生成章节内容
            chapter_result = await chapter_agent.run({
                "mode": "generate",
                "chapter_outline": request.chapter_outline,
                "world_setting": request.world_setting,
                "character_profiles": request.character_profiles,
                "previous_summary": request.previous_summary,
                "kb_context": request.kb_context,
                "writing_style": request.writing_style
            })

            chapter_content = chapter_result.get("chapter_content", "")
            if not chapter_content:
                print(f"第 {attempt + 1} 次生成失败：内容为空")
                continue

            # 质量评估
            quality_input = {
                "content_type": "chapter",
                "content": chapter_content,
                "context": {
                    "chapter_outline": request.chapter_outline,
                    "character_profiles": request.character_profiles,
                    "previous_chapters": request.previous_chapters,
                    "writing_style": request.writing_style
                }
            }
            print(f"质量检查输入: content_type={quality_input.get('content_type')}, content长度={len(quality_input.get('content', ''))}")
            quality_result = await quality_agent.run(quality_input)

            quality_score = quality_result.get("total_score", 0)
            print(f"第 {attempt + 1} 次生成质量评分: {quality_score}")

            generation_attempts.append({
                "attempt": attempt + 1,
                "content": chapter_content,
                "quality_score": quality_score,
                "quality_details": quality_result
            })

            # 更新最佳结果
            if quality_score > best_score:
                best_score = quality_score
                best_result = {
                    "content": chapter_content,
                    "quality_result": quality_result,
                    "attempt": attempt + 1
                }

            # 如果质量足够好，提前结束
            if quality_score >= 85:
                print(f"质量评分达到 {quality_score}，提前结束生成")
                break

        if not best_result:
            raise HTTPException(status_code=500, detail="所有生成尝试都失败了")

        # 保存最佳章节到数据库
        from app.db.repositories import ChapterRepository

        db_gen = get_db()
        db = next(db_gen)
        try:
            chapter_repo = ChapterRepository(db)
            chapter = chapter_repo.create(
                project_id=project_id,
                chapter_number=request.chapter_outline.get("number", 1),
                title=request.chapter_outline.get("title", f"第{request.chapter_outline.get('number', 1)}章"),
                content=best_result["content"],
                outline=request.chapter_outline,
                writing_style=request.writing_style,
                word_count=len(best_result["content"]),
                quality_score=best_score,
                evaluation_result=best_result["quality_result"],
                generation_metadata={
                    "attempts": len(generation_attempts),
                    "best_attempt": best_result["attempt"],
                    "all_attempts": generation_attempts
                }
            )
        finally:
            db.close()

        print(f"成功生成高质量章节: {chapter.title}，质量评分: {best_score}")
        print(f"章节ID: {chapter.id}")
        print(f"章节号: {chapter.chapter_number}")
        print(f"内容长度: {len(chapter.content or '')}")

        response_data = {
            "id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "content": chapter.content,
            "word_count": chapter.word_count or len(chapter.content or ""),
            "writing_style": chapter.writing_style,
            "status": chapter.status or "draft",
            "quality_score": best_score,
            "evaluation_result": best_result["quality_result"],
            "generation_attempts": len(generation_attempts),
            "best_attempt": best_result["attempt"],
            "created_at": chapter.created_at if isinstance(chapter.created_at, str) else (chapter.created_at.isoformat() if chapter.created_at else None),
            "updated_at": chapter.updated_at if isinstance(chapter.updated_at, str) else (chapter.updated_at.isoformat() if chapter.updated_at else None)
        }

        print(f"返回响应数据（带质量检查）: {response_data}")
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"带质量检查的章节生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成章节时发生错误: {str(e)}")

@router.get("/projects/{project_id}/chapters/{chapter_id}")
async def get_chapter(
    project_id: str,
    chapter_id: str,
    db: Session = Depends(get_db)
):
    """获取单个章节详情"""
    try:
        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, ChapterRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        chapter_repo = ChapterRepository(db)
        chapter = chapter_repo.get_by_id(chapter_id)

        if not chapter or chapter.project_id != project_id:
            raise HTTPException(status_code=404, detail="章节不存在")

        return {
            "id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "content": chapter.content,
            "word_count": chapter.word_count,
            "writing_style": chapter.writing_style,
            "status": chapter.status or "draft"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取章节失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取章节时发生错误: {str(e)}")

@router.put("/projects/{project_id}/chapters/{chapter_id}")
async def update_chapter(
    project_id: str,
    chapter_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
):
    """更新章节"""
    try:
        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, ChapterRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        chapter_repo = ChapterRepository(db)
        chapter = chapter_repo.get_by_id(chapter_id)

        if not chapter or chapter.project_id != project_id:
            raise HTTPException(status_code=404, detail="章节不存在")

        # 更新章节
        updated_chapter = chapter_repo.update(chapter_id, **update_data)

        return {
            "id": updated_chapter.id,
            "chapter_number": updated_chapter.chapter_number,
            "title": updated_chapter.title,
            "content": updated_chapter.content,
            "word_count": updated_chapter.word_count,
            "writing_style": updated_chapter.writing_style,
            "status": updated_chapter.status or "draft"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新章节失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"更新章节时发生错误: {str(e)}")

@router.post("/projects/{project_id}/chapters/{chapter_id}/polish")
async def polish_chapter(
    project_id: str,
    chapter_id: str,
    polish_data: dict,
    db: Session = Depends(get_db)
):
    """润色章节"""
    try:
        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, ChapterRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        chapter_repo = ChapterRepository(db)
        chapter = chapter_repo.get_by_id(chapter_id)

        if not chapter or chapter.project_id != project_id:
            raise HTTPException(status_code=404, detail="章节不存在")

        # 使用StylePolisherAgent润色章节
        from app.agents.style_polisher import StylePolisherAgent
        from app.core.llm import OpenAILLM

        agent = StylePolisherAgent(llm=OpenAILLM(), project_id=project_id)

        # 调用智能体润色章节内容
        result = await agent.run({
            "content": chapter.content,
            "style": chapter.writing_style or "流畅自然，细腻生动",
            "focus_areas": ["描写", "对话", "情感"]
        })

        # 更新章节内容
        chapter_repo.update(chapter.id, {
            "content": result["polished_content"]
        })

        return {
            "id": chapter.id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "content": result["polished_content"],
            "word_count": len(result["polished_content"]),
            "writing_style": chapter.writing_style,
            "status": chapter.status or "draft",
            "changes_summary": result.get("changes_summary", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"润色章节失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"润色章节时发生错误: {str(e)}")

@router.post("/projects/{project_id}/chapters/{chapter_id}/branches")
async def generate_plot_branches(
    project_id: str,
    chapter_id: str,
    branch_data: dict,
    db: Session = Depends(get_db)
):
    """生成剧情分支"""
    try:
        # 验证项目是否存在
        from app.db.repositories import ProjectRepository, ChapterRepository

        project_repo = ProjectRepository(db)
        project = project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        chapter_repo = ChapterRepository(db)
        chapter = chapter_repo.get_by_id(chapter_id)

        if not chapter or chapter.project_id != project_id:
            raise HTTPException(status_code=404, detail="章节不存在")

        # 获取项目相关数据
        from app.db.repositories import ConceptRepository, WorldSettingRepository, CharacterRepository

        concept_repo = ConceptRepository(db)
        world_setting_repo = WorldSettingRepository(db)
        character_repo = CharacterRepository(db)

        # 获取选中的概述、世界观和人物设定
        selected_concept = concept_repo.get_selected_by_project_id(project_id)
        selected_world_setting = world_setting_repo.get_selected_by_project_id(project_id)
        selected_character = character_repo.get_selected_by_project_id(project_id)

        # 使用ChapterChroniclerAgent生成剧情分支
        from app.agents.chapter_chronicler import ChapterChroniclerAgent
        from app.core.llm import OpenAILLM

        agent = ChapterChroniclerAgent(llm=OpenAILLM(), project_id=project_id)

        # 调用智能体生成剧情分支
        result = await agent.run({
            "mode": "branches",
            "chapter_outline": chapter.outline or {},
            "world_setting": selected_world_setting.content if selected_world_setting else {},
            "character_profiles": [selected_character.content] if selected_character else [],
            "previous_summary": branch_data.get("previous_summary", ""),
            "kb_context": branch_data.get("kb_context", [])
        })

        return {
            "plot_branches": result.get("plot_branches", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"生成剧情分支失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成剧情分支时发生错误: {str(e)}")
