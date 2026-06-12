from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.dependencies import get_workspace
from app.schemas.projects import (
    DeleteProjectResponse,
    ProjectCreateRequest,
    ProjectDetailResponse,
    ProjectSummaryResponse,
    ProjectUpdateRequest,
    RestoreVersionResponse,
    ScriptVersionCreateRequest,
    ScriptVersionDetailResponse,
    ScriptVersionSummaryResponse,
)
from app.services.export_service import export_project_json, export_project_markdown, export_project_yaml
from app.services.pdf_export_service import export_project_pdf
from app.services.project_service import (
    create_project,
    create_version,
    delete_project,
    get_project_detail,
    get_version_detail,
    list_projects,
    list_versions,
    restore_version,
    update_project,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectSummaryResponse,
    summary="创建项目",
    description="保存剧本项目到本地数据库，包含标题、类型、原始小说内容和生成的 YAML",
)
def create_project_endpoint(
    payload: ProjectCreateRequest,
    workspace: str = Depends(get_workspace),
) -> ProjectSummaryResponse:
    """创建新的剧本项目"""
    return create_project(payload, workspace)


@router.get(
    "",
    response_model=list[ProjectSummaryResponse],
    summary="获取项目列表",
    description="返回所有已保存项目的摘要信息（ID、标题、类型、创建时间、更新时间）",
)
def list_projects_endpoint(
    workspace: str = Depends(get_workspace),
) -> list[ProjectSummaryResponse]:
    """获取所有项目列表"""
    return list_projects(workspace)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="获取项目详情",
    description="返回指定项目的完整信息，包含小说内容、YAML 剧本、校验结果等",
)
def get_project_endpoint(
    project_id: int,
    workspace: str = Depends(get_workspace),
) -> ProjectDetailResponse:
    """获取项目详细信息"""
    return get_project_detail(project_id, workspace)


@router.put(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="更新项目",
    description="更新项目的 YAML 内容和校验结果，通常在编辑器中修改后调用",
)
def update_project_endpoint(
    project_id: int,
    payload: ProjectUpdateRequest,
    workspace: str = Depends(get_workspace),
) -> ProjectDetailResponse:
    """更新项目内容"""
    return update_project(project_id, payload, workspace)


@router.delete(
    "/{project_id}",
    response_model=DeleteProjectResponse,
    summary="删除项目",
    description="删除指定项目及其所有版本快照",
)
def delete_project_endpoint(
    project_id: int,
    workspace: str = Depends(get_workspace),
) -> dict[str, int | str]:
    """删除项目"""
    return delete_project(project_id, workspace)


@router.post(
    "/{project_id}/versions",
    response_model=ScriptVersionSummaryResponse,
    summary="创建版本快照",
    description="为项目创建版本快照，保存当前 YAML 状态，支持后续恢复",
)
def create_version_endpoint(
    project_id: int,
    payload: ScriptVersionCreateRequest,
    workspace: str = Depends(get_workspace),
) -> ScriptVersionSummaryResponse:
    """创建版本快照"""
    return create_version(project_id, payload, workspace)


@router.get(
    "/{project_id}/versions",
    response_model=list[ScriptVersionSummaryResponse],
    summary="获取版本列表",
    description="返回指定项目的所有版本快照",
)
def list_versions_endpoint(
    project_id: int,
    workspace: str = Depends(get_workspace),
) -> list[ScriptVersionSummaryResponse]:
    """获取项目版本列表"""
    return list_versions(project_id, workspace)


@router.get(
    "/{project_id}/versions/{version_id}",
    response_model=ScriptVersionDetailResponse,
    summary="获取版本详情",
    description="返回指定版本的完整 YAML 内容和校验结果",
)
def get_version_endpoint(
    project_id: int,
    version_id: int,
    workspace: str = Depends(get_workspace),
) -> ScriptVersionDetailResponse:
    """获取版本详细信息"""
    return get_version_detail(project_id, version_id, workspace)


@router.post(
    "/{project_id}/versions/{version_id}/restore",
    response_model=RestoreVersionResponse,
    summary="恢复版本",
    description="将项目恢复到指定版本的 YAML 状态",
)
def restore_version_endpoint(
    project_id: int,
    version_id: int,
    workspace: str = Depends(get_workspace),
) -> RestoreVersionResponse:
    """恢复到指定版本"""
    return restore_version(project_id, version_id, workspace)


@router.get(
    "/{project_id}/export/yaml",
    summary="导出为 YAML",
    description="导出项目的 YAML 剧本文件，文件名格式：`{title}.yaml`",
)
def export_yaml_endpoint(
    project_id: int,
    workspace: str = Depends(get_workspace),
) -> Response:
    """导出 YAML 格式"""
    return export_project_yaml(project_id, workspace)


@router.get(
    "/{project_id}/export/json", summary="导出为 JSON", description="解析 YAML 后导出为 JSON 格式，便于程序处理"
)
def export_json_endpoint(
    project_id: int,
    workspace: str = Depends(get_workspace),
) -> Response:
    """导出 JSON 格式"""
    return export_project_json(project_id, workspace)


@router.get(
    "/{project_id}/export/markdown",
    summary="导出为 Markdown",
    description="导出为人类可读的 Markdown 格式，包含标题、角色表、场景列表、完整对白",
)
def export_markdown_endpoint(
    project_id: int,
    workspace: str = Depends(get_workspace),
) -> Response:
    """导出 Markdown 格式"""
    return export_project_markdown(project_id, workspace)


@router.get(
    "/{project_id}/export/pdf",
    summary="导出为 PDF",
    description="导出为专业格式的 PDF 剧本，包含封面、角色表、场景详情、完整对白",
    responses={
        200: {"description": "PDF 文件", "content": {"application/pdf": {}}},
        400: {"description": "YAML 解析失败"},
        404: {"description": "项目不存在"},
    },
)
def export_pdf_endpoint(
    project_id: int,
    workspace: str = Depends(get_workspace),
) -> Response:
    """导出 PDF 格式"""
    from app.services.export_service import _build_filename, _content_disposition

    project = get_project_detail(project_id, workspace)
    pdf_bytes = export_project_pdf(project)

    filename = _build_filename(project.title, "pdf")
    headers = {"Content-Disposition": _content_disposition(filename)}

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
