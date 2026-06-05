from pydantic import BaseModel, Field


class ChapterResponse(BaseModel):
    id: str
    title: str
    content: str
    word_count: int


class ParseChaptersResponse(BaseModel):
    chapter_count: int
    valid: bool
    message: str
    chapters: list[ChapterResponse]
    warnings: list[str] = Field(default_factory=list)


class ValidationResponse(BaseModel):
    valid: bool
    errors: list[str]


class GenerateScriptResponse(BaseModel):
    yaml: str
    validation: ValidationResponse
