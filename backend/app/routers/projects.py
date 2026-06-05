from fastapi import APIRouter
from fastapi.responses import Response

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


@router.post("", response_model=ProjectSummaryResponse)
def create_project_endpoint(payload: ProjectCreateRequest) -> ProjectSummaryResponse:
    return create_project(payload)


@router.get("", response_model=list[ProjectSummaryResponse])
def list_projects_endpoint() -> list[ProjectSummaryResponse]:
    return list_projects()


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project_endpoint(project_id: int) -> ProjectDetailResponse:
    return get_project_detail(project_id)


@router.put("/{project_id}", response_model=ProjectDetailResponse)
def update_project_endpoint(project_id: int, payload: ProjectUpdateRequest) -> ProjectDetailResponse:
    return update_project(project_id, payload)


@router.delete("/{project_id}", response_model=DeleteProjectResponse)
def delete_project_endpoint(project_id: int) -> dict[str, int | str]:
    return delete_project(project_id)


@router.post("/{project_id}/versions", response_model=ScriptVersionSummaryResponse)
def create_version_endpoint(project_id: int, payload: ScriptVersionCreateRequest) -> ScriptVersionSummaryResponse:
    return create_version(project_id, payload)


@router.get("/{project_id}/versions", response_model=list[ScriptVersionSummaryResponse])
def list_versions_endpoint(project_id: int) -> list[ScriptVersionSummaryResponse]:
    return list_versions(project_id)


@router.get("/{project_id}/versions/{version_id}", response_model=ScriptVersionDetailResponse)
def get_version_endpoint(project_id: int, version_id: int) -> ScriptVersionDetailResponse:
    return get_version_detail(project_id, version_id)


@router.post("/{project_id}/versions/{version_id}/restore", response_model=RestoreVersionResponse)
def restore_version_endpoint(project_id: int, version_id: int) -> RestoreVersionResponse:
    return restore_version(project_id, version_id)


@router.get("/{project_id}/export/yaml")
def export_yaml_endpoint(project_id: int) -> Response:
    return export_project_yaml(project_id)


@router.get("/{project_id}/export/json")
def export_json_endpoint(project_id: int) -> Response:
    return export_project_json(project_id)


@router.get("/{project_id}/export/markdown")
def export_markdown_endpoint(project_id: int) -> Response:
    return export_project_markdown(project_id)
