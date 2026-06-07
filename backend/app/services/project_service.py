import json
from datetime import datetime, timezone
from sqlite3 import Row

from fastapi import HTTPException, status

from app.db.database import get_connection
from app.schemas.projects import (
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectSummaryResponse,
    ProjectUpdateRequest,
    RestoreVersionResponse,
    ScriptVersionCreateRequest,
    ScriptVersionDetailResponse,
    ScriptVersionSummaryResponse,
)
from app.schemas.requests import ChapterInput
from app.schemas.responses import ValidationResponse
from app.services.script_validator import validate_script_yaml


def create_project(payload: ProjectCreateRequest, workspace: str = "default") -> ProjectSummaryResponse:
    validation = validate_script_yaml(payload.yaml)
    now = _now()
    chapters_json = json.dumps([chapter.model_dump() for chapter in payload.chapters], ensure_ascii=False)
    validation_json = _validation_to_json(validation)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO projects (
                title, genre, source_content, chapter_count, chapters_json,
                current_yaml, validation_json, generation_mode,
                created_at, updated_at, workspace
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.title.strip(),
                payload.genre.strip(),
                payload.source_content,
                len(payload.chapters),
                chapters_json,
                payload.yaml,
                validation_json,
                payload.generation_mode,
                now,
                now,
                workspace,
            ),
        )
        connection.commit()
        project_id = int(cursor.lastrowid)

    return get_project_summary(project_id, workspace)


def list_projects(workspace: str = "default") -> list[ProjectSummaryResponse]:
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, title, genre, chapter_count, generation_mode, created_at, updated_at
            FROM projects
            WHERE workspace = ?
            ORDER BY updated_at DESC, id DESC
            """, (workspace,)).fetchall()
    return [_row_to_summary(row) for row in rows]


def get_project_summary(project_id: int, workspace: str = "default") -> ProjectSummaryResponse:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, genre, chapter_count, generation_mode, created_at, updated_at
            FROM projects
            WHERE id = ? AND workspace = ?
            """,
            (project_id, workspace),
        ).fetchone()
    if row is None:
        _raise_project_not_found(project_id)
    return _row_to_summary(row)


def get_project_detail(project_id: int, workspace: str = "default") -> ProjectDetailResponse:
    row = _get_project_row(project_id, workspace)
    return _row_to_detail(row)


def update_project(project_id: int, payload: ProjectUpdateRequest, workspace: str = "default") -> ProjectDetailResponse:
    current = _get_project_row(project_id, workspace)

    title = payload.title.strip() if payload.title is not None else current["title"]
    genre = payload.genre.strip() if payload.genre is not None else current["genre"]
    source_content = payload.source_content if payload.source_content is not None else current["source_content"]
    chapters = payload.chapters if payload.chapters is not None else _load_chapters(current["chapters_json"])
    yaml_text = payload.yaml if payload.yaml is not None else current["current_yaml"]
    generation_mode = payload.generation_mode if payload.generation_mode is not None else current["generation_mode"]
    validation = validate_script_yaml(yaml_text)

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE projects
            SET title = ?, genre = ?, source_content = ?, chapter_count = ?, chapters_json = ?,
                current_yaml = ?, validation_json = ?, generation_mode = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                title,
                genre,
                source_content,
                len(chapters),
                json.dumps([chapter.model_dump() for chapter in chapters], ensure_ascii=False),
                yaml_text,
                _validation_to_json(validation),
                generation_mode,
                _now(),
                project_id,
            ),
        )
        connection.commit()

    return get_project_detail(project_id, workspace)


def delete_project(project_id: int, workspace: str = "default") -> dict[str, int | str]:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM projects WHERE id = ? AND workspace = ?",
            (project_id, workspace),
        )
        connection.commit()

    if cursor.rowcount == 0:
        _raise_project_not_found(project_id)

    return {"message": "项目已删除", "id": project_id}


def create_version(project_id: int, payload: ScriptVersionCreateRequest, workspace: str = "default") -> ScriptVersionSummaryResponse:
    _get_project_row(project_id, workspace)
    validation = validate_script_yaml(payload.yaml)
    now = _now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO script_versions (project_id, version_name, yaml, validation_json, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                payload.version_name.strip(),
                payload.yaml,
                _validation_to_json(validation),
                payload.note.strip(),
                now,
            ),
        )
        connection.commit()
        version_id = int(cursor.lastrowid)

    return get_version_detail(project_id, version_id, workspace)


def list_versions(project_id: int, workspace: str = "default") -> list[ScriptVersionSummaryResponse]:
    _get_project_row(project_id, workspace)
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, project_id, version_name, note, created_at
            FROM script_versions
            WHERE project_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (project_id,),
        ).fetchall()
    return [_row_to_version_summary(row) for row in rows]


def get_version_detail(project_id: int, version_id: int, workspace: str = "default") -> ScriptVersionDetailResponse:
    row = _get_version_row(project_id, version_id, workspace)
    return ScriptVersionDetailResponse(
        id=row["id"],
        project_id=row["project_id"],
        version_name=row["version_name"],
        note=row["note"],
        created_at=datetime.fromisoformat(row["created_at"]),
        yaml=row["yaml"],
        validation=_load_validation(row["validation_json"]),
    )


def restore_version(project_id: int, version_id: int, workspace: str = "default") -> RestoreVersionResponse:
    version = _get_version_row(project_id, version_id, workspace)

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE projects
            SET current_yaml = ?, validation_json = ?, updated_at = ?
            WHERE id = ?
            """,
            (version["yaml"], version["validation_json"], _now(), project_id),
        )
        connection.commit()

    detail = get_project_detail(project_id, workspace)
    return RestoreVersionResponse(**detail.model_dump(), restored_from_version=version_id)


def _get_project_row(project_id: int, workspace: str = "default") -> Row:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM projects WHERE id = ? AND workspace = ?",
            (project_id, workspace),
        ).fetchone()
    if row is None:
        _raise_project_not_found(project_id)
    return row


def _get_version_row(project_id: int, version_id: int, workspace: str = "default") -> Row:
    _get_project_row(project_id, workspace)
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM script_versions WHERE id = ? AND project_id = ?",
            (version_id, project_id),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"版本不存在：{version_id}")
    return row


def _row_to_summary(row: Row) -> ProjectSummaryResponse:
    return ProjectSummaryResponse(
        id=row["id"],
        title=row["title"],
        genre=row["genre"],
        chapter_count=row["chapter_count"],
        generation_mode=row["generation_mode"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _row_to_detail(row: Row) -> ProjectDetailResponse:
    return ProjectDetailResponse(
        **_row_to_summary(row).model_dump(),
        source_content=row["source_content"],
        chapters=_load_chapters(row["chapters_json"]),
        current_yaml=row["current_yaml"],
        validation=_load_validation(row["validation_json"]),
    )


def _row_to_version_summary(row: Row) -> ScriptVersionSummaryResponse:
    return ScriptVersionSummaryResponse(
        id=row["id"],
        project_id=row["project_id"],
        version_name=row["version_name"],
        note=row["note"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _load_chapters(value: str) -> list[ChapterInput]:
    try:
        raw_chapters = json.loads(value)
    except json.JSONDecodeError:
        raw_chapters = []
    return [ChapterInput(**chapter) for chapter in raw_chapters]


def _load_validation(value: str) -> ValidationResponse:
    try:
        raw_validation = json.loads(value)
    except json.JSONDecodeError:
        raw_validation = {"valid": False, "errors": ["validation_json 解析失败"]}
    return ValidationResponse(**raw_validation)


def _validation_to_json(validation: ValidationResponse) -> str:
    return json.dumps(validation.model_dump(), ensure_ascii=False)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _raise_project_not_found(project_id: int) -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"项目不存在：{project_id}")
