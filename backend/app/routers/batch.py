"""
批量项目操作 API
支持批量删除、批量导出等操作
"""

from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.project_service import delete_project, get_project_detail

router = APIRouter(prefix="/api/batch", tags=["batch"])


class BatchDeleteRequest(BaseModel):
    project_ids: List[int]


class BatchDeleteResponse(BaseModel):
    deleted_count: int
    failed_ids: List[int]
    errors: List[str]


class BatchExportRequest(BaseModel):
    project_ids: List[int]
    format: str  # yaml, json, markdown, pdf


class BatchExportResponse(BaseModel):
    success_count: int
    failed_count: int
    download_urls: List[str]
    errors: List[str]


@router.post(
    "/delete",
    response_model=BatchDeleteResponse,
    summary="批量删除项目",
    description="一次性删除多个项目及其所有版本快照。最多支持 50 个项目。",
)
def batch_delete_projects(request: BatchDeleteRequest) -> BatchDeleteResponse:
    """批量删除项目"""
    if len(request.project_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="批量删除最多支持 50 个项目",
        )

    deleted_count = 0
    failed_ids = []
    errors = []

    for project_id in request.project_ids:
        try:
            delete_project(project_id)
            deleted_count += 1
        except HTTPException as exc:
            failed_ids.append(project_id)
            errors.append(f"项目 {project_id}: {exc.detail}")
        except Exception as exc:
            failed_ids.append(project_id)
            errors.append(f"项目 {project_id}: {str(exc)}")

    return BatchDeleteResponse(
        deleted_count=deleted_count,
        failed_ids=failed_ids,
        errors=errors,
    )


@router.post(
    "/validate",
    summary="批量校验项目",
    description="批量校验多个项目的 YAML 剧本。返回每个项目的校验结果。",
)
def batch_validate_projects(request: BatchDeleteRequest) -> dict:
    """批量校验项目"""
    if len(request.project_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="批量校验最多支持 50 个项目",
        )

    from app.services.script_validator import validate_script_yaml

    results = []

    for project_id in request.project_ids:
        try:
            project = get_project_detail(project_id)
            validation = validate_script_yaml(project.current_yaml)

            results.append(
                {
                    "project_id": project_id,
                    "title": project.title,
                    "valid": validation.valid,
                    "error_count": len(validation.errors),
                    "errors": validation.errors[:3] if not validation.valid else [],  # 只返回前3个错误
                }
            )
        except Exception as exc:
            results.append(
                {
                    "project_id": project_id,
                    "title": "未知",
                    "valid": False,
                    "error_count": 1,
                    "errors": [str(exc)],
                }
            )

    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count

    return {
        "total": len(results),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "results": results,
    }


@router.get(
    "/stats",
    summary="获取项目统计信息",
    description="返回项目总览统计：总数、类型分布、生成模式分布等",
)
def get_batch_stats() -> dict:
    """获取批量统计信息"""
    from app.db.database import get_connection

    with get_connection() as conn:
        cursor = conn.cursor()

        # 总项目数
        cursor.execute("SELECT COUNT(*) FROM projects")
        total_count = cursor.fetchone()[0]

        # 按类型统计
        cursor.execute("SELECT genre, COUNT(*) FROM projects GROUP BY genre ORDER BY COUNT(*) DESC")
        genre_stats = [{"genre": row[0], "count": row[1]} for row in cursor.fetchall()]

        # 按生成模式统计
        cursor.execute("SELECT generation_mode, COUNT(*) FROM projects GROUP BY generation_mode")
        mode_stats = [{"mode": row[0], "count": row[1]} for row in cursor.fetchall()]

        # 平均章节数
        cursor.execute("SELECT AVG(chapter_count) FROM projects")
        avg_chapters = cursor.fetchone()[0] or 0

        # 最近创建的5个项目
        cursor.execute("""
            SELECT id, title, genre, created_at
            FROM projects
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_projects = [
            {
                "id": row[0],
                "title": row[1],
                "genre": row[2],
                "created_at": row[3],
            }
            for row in cursor.fetchall()
        ]

        return {
            "total_count": total_count,
            "avg_chapters": round(avg_chapters, 1),
            "genre_distribution": genre_stats,
            "mode_distribution": mode_stats,
            "recent_projects": recent_projects,
        }
