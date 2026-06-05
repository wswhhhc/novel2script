from pydantic import BaseModel, Field


class ParseChaptersRequest(BaseModel):
    content: str = Field(..., min_length=1)


class ValidateScriptRequest(BaseModel):
    yaml: str = Field(..., min_length=1)


class ChapterInput(BaseModel):
    id: str
    title: str
    content: str = Field(..., min_length=1)
    word_count: int = Field(..., ge=0)


class GenerateScriptRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=50)
    chapters: list[ChapterInput]
