from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.requests import ChapterInput
from app.schemas.responses import ValidationResponse


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=50)
    source_content: str = Field(..., min_length=1)
    chapters: list[ChapterInput] = Field(default_factory=list)
    yaml: str = Field(..., min_length=1)
    validation: ValidationResponse | dict[str, Any] | None = None
    generation_mode: str = Field(default="mock", pattern="^(mock|ai)$")


class ProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    genre: str | None = Field(default=None, min_length=1, max_length=50)
    source_content: str | None = Field(default=None, min_length=1)
    chapters: list[ChapterInput] | None = None
    yaml: str | None = Field(default=None, min_length=1)
    validation: ValidationResponse | dict[str, Any] | None = None
    generation_mode: str | None = Field(default=None, pattern="^(mock|ai)$")


class ProjectSummaryResponse(BaseModel):
    id: int
    title: str
    genre: str
    chapter_count: int
    generation_mode: str
    created_at: datetime
    updated_at: datetime


class ProjectDetailResponse(ProjectSummaryResponse):
    source_content: str
    chapters: list[ChapterInput]
    current_yaml: str
    validation: ValidationResponse


class DeleteProjectResponse(BaseModel):
    message: str
    id: int


class ScriptVersionCreateRequest(BaseModel):
    version_name: str = Field(..., min_length=1, max_length=100)
    yaml: str = Field(..., min_length=1)
    validation: ValidationResponse | dict[str, Any] | None = None
    note: str = Field(default="", max_length=500)


class ScriptVersionSummaryResponse(BaseModel):
    id: int
    project_id: int
    version_name: str
    note: str
    created_at: datetime


class ScriptVersionDetailResponse(ScriptVersionSummaryResponse):
    yaml: str
    validation: ValidationResponse


class RestoreVersionResponse(ProjectDetailResponse):
    restored_from_version: int
