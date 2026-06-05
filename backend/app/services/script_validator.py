import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from app.config.settings import settings
from app.schemas.responses import ValidationResponse


def validate_script_yaml(yaml_text: str, schema_path: Path | None = None) -> ValidationResponse:
    errors: list[str] = []

    try:
        parsed = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return ValidationResponse(valid=False, errors=[f"YAML 语法错误：{exc}"])

    if parsed is None:
        return ValidationResponse(valid=False, errors=["YAML 内容为空"])

    schema_file = schema_path or settings.schema_path
    try:
        with schema_file.open("r", encoding="utf-8") as file:
            schema = json.load(file)
    except FileNotFoundError:
        return ValidationResponse(valid=False, errors=[f"Schema 文件不存在：{schema_file}"])
    except json.JSONDecodeError as exc:
        return ValidationResponse(valid=False, errors=[f"Schema JSON 解析失败：{exc}"])

    try:
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        schema_errors = sorted(validator.iter_errors(parsed), key=lambda error: list(error.path))
    except SchemaError as exc:
        return ValidationResponse(valid=False, errors=[f"Schema 定义错误：{exc.message}"])

    for error in schema_errors:
        path = _format_path(error.path)
        errors.append(f"{path}: {error.message}")

    errors.extend(_validate_business_rules(parsed))
    return ValidationResponse(valid=not errors, errors=errors)


def _validate_business_rules(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["根节点必须是对象"]

    script = document.get("script")
    if not isinstance(script, dict):
        return ["script 必须是对象"]

    source = script.get("source") if isinstance(script.get("source"), dict) else {}
    chapters = source.get("chapters") if isinstance(source.get("chapters"), list) else []
    characters = script.get("characters") if isinstance(script.get("characters"), list) else []
    scenes = script.get("scenes") if isinstance(script.get("scenes"), list) else []

    errors: list[str] = []
    chapter_ids, duplicate_chapter_ids = _collect_ids(chapters)
    character_ids, duplicate_character_ids = _collect_ids(characters)
    scene_ids, duplicate_scene_ids = _collect_ids(scenes)
    chapter_count = source.get("chapter_count")
    created_at = script.get("created_at")

    if isinstance(chapter_count, int) and chapter_count != len(chapters):
        errors.append(f"source.chapter_count 与 chapters 数量不一致：{chapter_count} != {len(chapters)}")
    if isinstance(created_at, str) and not _is_iso_datetime(created_at):
        errors.append(f"created_at 不是合法的 ISO 8601 date-time：{created_at}")

    for chapter_id in duplicate_chapter_ids:
        errors.append(f"chapter id 不唯一：{chapter_id}")
    for character_id in duplicate_character_ids:
        errors.append(f"character id 不唯一：{character_id}")
    for scene_id in duplicate_scene_ids:
        errors.append(f"scene id 不唯一：{scene_id}")

    for character in characters:
        if not isinstance(character, dict):
            continue
        character_id = character.get("id", "<unknown>")
        first_appearance = character.get("first_appearance")
        if first_appearance and first_appearance not in chapter_ids:
            errors.append(f"角色 {character_id} 的 first_appearance 引用了不存在的章节：{first_appearance}")
        for relationship in _as_list(character.get("relationships")):
            if not isinstance(relationship, dict):
                continue
            related_id = relationship.get("character_id")
            if related_id and related_id not in character_ids:
                errors.append(f"角色 {character_id} 的 relationships 引用了不存在的角色：{related_id}")

    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("id", "<unknown>")
        for chapter_id in _as_list(scene.get("source_chapters")):
            if chapter_id not in chapter_ids:
                errors.append(f"场景 {scene_id} 的 source_chapters 引用了不存在的章节：{chapter_id}")
        for character_id in _as_list(scene.get("characters")):
            if character_id not in character_ids:
                errors.append(f"场景 {scene_id} 的 characters 引用了不存在的角色：{character_id}")
        for beat_index, beat in enumerate(_as_list(scene.get("beats")), start=1):
            if not isinstance(beat, dict):
                continue
            if beat.get("type") == "dialogue":
                character_id = beat.get("character")
                if character_id and character_id not in character_ids:
                    errors.append(
                        f"场景 {scene_id} 第 {beat_index} 个 dialogue beat 引用了不存在的角色：{character_id}"
                    )

    return errors


def _collect_ids(items: list[Any]) -> tuple[set[str], list[str]]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str):
            continue
        if item_id in seen and item_id not in duplicates:
            duplicates.append(item_id)
        seen.add(item_id)
    return seen, duplicates


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _format_path(path: Any) -> str:
    parts = [str(part) for part in path]
    return ".".join(parts) if parts else "$"


def _is_iso_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True
