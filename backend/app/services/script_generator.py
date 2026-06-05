"""
剧本生成服务
实现分阶段 AI 生成流程：章节分析 -> 角色提取 -> 场景规划 -> 剧本生成 -> YAML 修复
"""
import re

import yaml
from fastapi import HTTPException, status

from app.config.settings import settings
from app.schemas.requests import ChapterInput
from app.schemas.responses import GenerateScriptResponse
from app.services.ai_client import AIClientError, call_ai_model, parse_json_response
from app.services.prompt_loader import format_chapters_for_prompt, load_prompt_template
from app.services.script_validator import validate_script_yaml

CHAPTER_ID_RE = re.compile(r"^C[0-9]{3}$")
YAML_CODE_BLOCK_RE = re.compile(r"```(?:yaml|yml)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
AI_CHAPTER_PROMPT_LIMIT = 8_000


def generate_script_mock(title: str, genre: str, chapters: list[ChapterInput]) -> GenerateScriptResponse:
    """
    Mock 剧本生成（返回示例 YAML）
    用于前后端联调，不调用真实 AI
    """
    _validate_input(title, genre, chapters)

    try:
        yaml_text = settings.sample_output_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"示例 YAML 文件不存在：{settings.sample_output_path}",
        ) from exc

    validation = validate_script_yaml(yaml_text)
    return GenerateScriptResponse(yaml=yaml_text, validation=validation)


def generate_script_with_ai(title: str, genre: str, chapters: list[ChapterInput]) -> GenerateScriptResponse:
    """
    使用 AI 生成剧本（4 阶段流程）

    阶段 1: 章节分析 (01_chapter_analysis.txt)
    阶段 2: 角色提取 (02_character_extraction.txt)
    阶段 3: 场景规划 (03_scene_planning.txt)
    阶段 4: 剧本生成 (04_script_generation.txt)
    阶段 5: YAML 修复 (05_yaml_fix.txt，如果校验失败)

    Args:
        title: 小说标题
        genre: 剧本类型
        chapters: 章节列表

    Returns:
        GenerateScriptResponse 包含生成的 YAML 和校验结果

    Raises:
        HTTPException: 当输入验证失败或 AI 调用失败时
    """
    _validate_input(title, genre, chapters)

    try:
        # 准备章节数据
        chapters_data = [
            {"id": ch.id, "title": ch.title, "content": ch.content, "word_count": ch.word_count}
            for ch in chapters
        ]
        chapters_text = format_chapters_for_prompt(_trim_chapters_for_ai_prompt(chapters_data))

        # 阶段 1: 章节分析
        chapters_analysis = _stage_1_analyze_chapters(title, genre, chapters_text)

        # 阶段 2: 角色提取
        characters = _stage_2_extract_characters(title, genre, chapters_analysis)

        # 阶段 3: 场景规划
        scenes_outline = _stage_3_plan_scenes(title, genre, chapters_analysis, characters)

        # 阶段 4: 剧本生成
        yaml_text = _stage_4_generate_script(title, genre, chapters_text, chapters_analysis, characters, scenes_outline)

        # 阶段 5: 校验与修复
        validation = validate_script_yaml(yaml_text)
        if not validation.valid:
            yaml_text = _stage_5_fix_yaml(yaml_text, validation.errors)
            validation = validate_script_yaml(yaml_text)

        return GenerateScriptResponse(yaml=yaml_text, validation=validation)

    except AIClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 服务调用失败：{str(exc)}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"剧本生成过程出错：{str(exc)}",
        ) from exc


def _validate_input(title: str, genre: str, chapters: list[ChapterInput]) -> None:
    """验证输入参数"""
    if not title or not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="小说标题不能为空",
        )

    if len(chapters) < settings.min_chapters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"章节数量不足，需要至少 {settings.min_chapters} 个章节，当前收到 {len(chapters)} 个章节",
        )

    if len(chapters) > settings.max_chapters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"章节数量过多，最多支持 {settings.max_chapters} 个章节，当前收到 {len(chapters)} 个章节",
        )

    total_content_length = sum(len(chapter.content) for chapter in chapters)
    if total_content_length > settings.max_input_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"输入文本过长（{total_content_length} 字），超出上限 {settings.max_input_length} 字，请精简内容",
        )

    for index, chapter in enumerate(chapters, start=1):
        if not CHAPTER_ID_RE.fullmatch(chapter.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"第 {index} 个章节 ID 格式错误：{chapter.id}，应为 C001-C999",
            )


def _stage_1_analyze_chapters(title: str, genre: str, chapters_text: str) -> dict:
    """
    阶段 1: 章节分析
    使用 01_chapter_analysis.txt 提取摘要、人物、事件、地点等
    """
    prompt = load_prompt_template(
        "01_chapter_analysis.txt",
        title=title,
        genre=genre,
        chapters=chapters_text,
    )

    response = call_ai_model(prompt)
    return parse_json_response(response, stage_name="阶段 1 章节分析")


def _stage_2_extract_characters(title: str, genre: str, chapters_analysis: dict) -> dict:
    """
    阶段 2: 角色提取
    使用 02_character_extraction.txt 生成统一角色表
    """
    prompt = load_prompt_template(
        "02_character_extraction.txt",
        title=title,
        genre=genre,
        chapters_analysis=chapters_analysis,
    )

    response = call_ai_model(prompt)
    return parse_json_response(response, stage_name="阶段 2 角色提取")


def _stage_3_plan_scenes(title: str, genre: str, chapters_analysis: dict, characters: dict) -> dict:
    """
    阶段 3: 场景规划
    使用 03_scene_planning.txt 拆分场景并生成场景大纲
    """
    prompt = load_prompt_template(
        "03_scene_planning.txt",
        title=title,
        genre=genre,
        chapters_analysis=chapters_analysis,
        characters=characters,
    )

    response = call_ai_model(prompt)
    return parse_json_response(response, stage_name="阶段 3 场景规划")


def _stage_4_generate_script(
    title: str,
    genre: str,
    chapters_text: str,
    chapters_analysis: dict,
    characters: dict,
    scenes_outline: dict,
) -> str:
    """
    阶段 4: 剧本生成
    使用 04_script_generation.txt 生成完整 YAML 剧本
    """
    prompt = load_prompt_template(
        "04_script_generation.txt",
        title=title,
        genre=genre,
        chapters=chapters_text,
        chapters_analysis=chapters_analysis,
        characters=characters,
        scenes_outline=scenes_outline,
    )

    response = call_ai_model(prompt)

    return _extract_yaml_from_response(response, stage_name="阶段 4 剧本生成")


def _stage_5_fix_yaml(original_yaml: str, errors: list[str]) -> str:
    """
    阶段 5: YAML 修复
    使用 05_yaml_fix.txt 修复校验错误
    """
    schema_content = settings.schema_path.read_text(encoding="utf-8")
    errors_text = "\n".join(f"{i+1}. {error}" for i, error in enumerate(errors))

    for attempt in range(settings.auto_fix_attempts):
        prompt = load_prompt_template(
            "05_yaml_fix.txt",
            original_yaml=original_yaml,
            validation_errors=errors_text,
            schema_content=schema_content,
        )

        try:
            response = call_ai_model(prompt)
            fixed_yaml = _extract_yaml_from_response(response, stage_name=f"阶段 5 YAML 修复（第 {attempt + 1} 次）")

            # 检查是否修复成功
            validation = validate_script_yaml(fixed_yaml)
            if validation.valid:
                return fixed_yaml

            # 如果还有错误，继续下一轮修复
            original_yaml = fixed_yaml
            errors_text = "\n".join(f"{i+1}. {error}" for i, error in enumerate(validation.errors))

        except AIClientError:
            # 修复失败，继续下一轮
            continue

    # 修复失败，返回最后一次尝试的结果
    return original_yaml


def _extract_yaml_from_response(text: str, stage_name: str = "AI YAML 阶段") -> str:
    """
    从 AI 响应中提取 YAML 内容
    支持 Markdown 代码块、直接 YAML，以及 YAML 前后少量说明。
    """
    original_text = text
    text = text.strip()
    if not text:
        raise AIClientError(f"{stage_name} YAML 提取失败：模型返回为空")

    code_block = YAML_CODE_BLOCK_RE.search(text)
    if code_block:
        return _ensure_yaml_candidate(code_block.group(1).strip(), stage_name)

    if text.startswith("script:"):
        return _ensure_yaml_candidate(text, stage_name)

    extracted = _extract_from_script_root(text)
    if extracted:
        return _ensure_yaml_candidate(extracted, stage_name)

    snippet = " ".join(original_text.split())[:300]
    raise AIClientError(f"{stage_name} YAML 提取失败：未找到 script 顶层字段。响应片段：{snippet}")


def _extract_from_script_root(text: str) -> str | None:
    lines = text.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == "script:":
            start_index = index
            break

    if start_index is None:
        return None

    yaml_lines: list[str] = []
    for line in lines[start_index:]:
        if yaml_lines and line.strip() and not line.startswith((" ", "\t")) and line.strip() != "script:":
            break
        yaml_lines.append(line)

    return "\n".join(yaml_lines).strip()


def _ensure_yaml_candidate(yaml_text: str, stage_name: str) -> str:
    if "script:" not in yaml_text:
        raise AIClientError(f"{stage_name} YAML 提取失败：结果中缺少 script 顶层字段")

    try:
        yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise AIClientError(f"{stage_name} YAML 解析失败：{exc}") from exc

    return yaml_text


def _trim_chapters_for_ai_prompt(chapters: list[dict]) -> list[dict]:
    trimmed: list[dict] = []
    for chapter in chapters:
        content = chapter["content"]
        if len(content) <= AI_CHAPTER_PROMPT_LIMIT:
            trimmed.append(chapter)
            continue

        head_limit = AI_CHAPTER_PROMPT_LIMIT // 2
        tail_limit = AI_CHAPTER_PROMPT_LIMIT - head_limit
        omitted = len(content) - AI_CHAPTER_PROMPT_LIMIT
        trimmed.append(
            {
                **chapter,
                "content": (
                    content[:head_limit]
                    + f"\n\n[本章过长，已省略中间 {omitted} 字；请基于前后关键片段提取摘要、事件和对白线索]\n\n"
                    + content[-tail_limit:]
                ),
            }
        )
    return trimmed
