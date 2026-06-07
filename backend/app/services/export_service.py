import json
import re
from urllib.parse import quote
from typing import Any

import yaml
from fastapi import HTTPException, Response, status

from app.services.project_service import get_project_detail

FILENAME_SAFE_RE = re.compile(r'[\\/:*?"<>|\s]+')
ASCII_FILENAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def export_project_yaml(project_id: int, workspace: str = "default") -> Response:
    project = get_project_detail(project_id, workspace)
    filename = _build_filename(project.title, "yaml")
    return Response(
        content=project.current_yaml,
        media_type="text/yaml; charset=utf-8",
        headers={"Content-Disposition": _content_disposition(filename)},
    )


def export_project_json(project_id: int, workspace: str = "default") -> Response:
    project = get_project_detail(project_id, workspace)
    document = _parse_yaml(project.current_yaml)
    filename = _build_filename(project.title, "json")
    return Response(
        content=json.dumps(document, ensure_ascii=False, indent=2),
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": _content_disposition(filename)},
    )


def export_project_markdown(project_id: int, workspace: str = "default") -> Response:
    project = get_project_detail(project_id, workspace)
    document = _parse_yaml(project.current_yaml)
    markdown = _to_markdown(document)
    filename = _build_filename(project.title, "md")
    return Response(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": _content_disposition(filename)},
    )


def _parse_yaml(yaml_text: str) -> Any:
    try:
        document = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"YAML 无法解析，不能导出：{exc}",
        ) from exc

    if document is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="YAML 内容为空，不能导出")
    return document


def _to_markdown(document: Any) -> str:
    script = document.get("script", {}) if isinstance(document, dict) else {}
    title = _text(script.get("title"), "未命名剧本")
    genre = _text(script.get("genre"), "未分类")
    logline = _text(script.get("logline"), "")
    source = script.get("source", {}) if isinstance(script.get("source"), dict) else {}
    chapters = source.get("chapters", []) if isinstance(source.get("chapters"), list) else []
    characters = script.get("characters", []) if isinstance(script.get("characters"), list) else []
    scenes = script.get("scenes", []) if isinstance(script.get("scenes"), list) else []
    notes = script.get("adaptation_notes", []) if isinstance(script.get("adaptation_notes"), list) else []

    lines = [f"# {title}", "", f"- 类型：{genre}", f"- 来源章节数：{_text(source.get('chapter_count'), len(chapters))}"]
    if logline:
        lines.extend(["", "## 一句话梗概", "", logline])

    lines.extend(["", "## 来源章节", ""])
    if chapters:
        for chapter in chapters:
            if isinstance(chapter, dict):
                lines.append(f"- `{_text(chapter.get('id'), '')}` {_text(chapter.get('title'), '未命名章节')}")
    else:
        lines.append("- 未提供章节信息")

    lines.extend(["", "## 角色表", "", "| ID | 姓名 | 简介 |", "| --- | --- | --- |"])
    if characters:
        for character in characters:
            if isinstance(character, dict):
                char_id = _text(character.get("id"), "")
                char_name = _text(character.get("name"), "")
                char_desc = _text(character.get("description"), "")
                lines.append(f"| {char_id} | {char_name} | {char_desc} |")
    else:
        lines.append("| - | - | 未提供角色信息 |")

    lines.extend(["", "## 场景列表", ""])
    if scenes:
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            lines.append(f"### {_text(scene.get('id'), '')} {_text(scene.get('title'), '未命名场景')}")
            lines.append("")
            lines.append(f"- 地点：{_text(scene.get('location'), '未指定')}")
            lines.append(f"- 时间：{_text(scene.get('time'), '未指定')}")
            lines.append(f"- 来源章节：{', '.join(_as_text_list(scene.get('source_chapters'))) or '未指定'}")
            lines.append(f"- 出场角色：{', '.join(_as_text_list(scene.get('characters'))) or '未指定'}")
            if scene.get("summary"):
                lines.extend(["", _text(scene.get("summary"), "")])
            beats = scene.get("beats") if isinstance(scene.get("beats"), list) else []
            if beats:
                lines.extend(["", "#### 剧情节拍"])
                for beat in beats:
                    if isinstance(beat, dict):
                        speaker = f"{_text(beat.get('character'), '')}：" if beat.get("character") else ""
                        lines.append(f"- [{_text(beat.get('type'), 'note')}] {speaker}{_text(beat.get('text'), '')}")
            lines.append("")
    else:
        lines.append("- 未提供场景信息")

    lines.extend(["", "## 改编说明", ""])
    if notes:
        for note in notes:
            if isinstance(note, dict):
                lines.append(f"- [{_text(note.get('type'), 'note')}] {_text(note.get('description'), '')}")
            else:
                lines.append(f"- {_text(note, '')}")
    else:
        lines.append("- 暂无改编说明")

    return "\n".join(lines).strip() + "\n"


def _build_filename(title: str, extension: str) -> str:
    normalized = FILENAME_SAFE_RE.sub("_", title.strip()).strip("_")
    return f"{normalized or 'novel2script'}_script.{extension}"


def _content_disposition(filename: str) -> str:
    fallback = ASCII_FILENAME_RE.sub("_", filename).strip("_") or "novel2script_script"
    return f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename)}"


def _text(value: Any, fallback: Any = "") -> str:
    if value is None:
        return str(fallback)
    return str(value).replace("|", "\\|").strip()


def _as_text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if item is not None]
