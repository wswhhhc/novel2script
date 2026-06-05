from fastapi import APIRouter

from app.schemas.requests import ParseChaptersRequest
from app.schemas.responses import ChapterResponse, ParseChaptersResponse
from app.services.chapter_parser import parse_chapters

router = APIRouter(prefix="/api/chapters", tags=["chapters"])


@router.post("/parse", response_model=ParseChaptersResponse)
def parse_chapters_endpoint(request: ParseChaptersRequest) -> ParseChaptersResponse:
    result = parse_chapters(request.content)
    return ParseChaptersResponse(
        chapter_count=result.chapter_count,
        valid=result.valid,
        message=result.message,
        warnings=result.warnings,
        chapters=[
            ChapterResponse(
                id=chapter.id,
                title=chapter.title,
                content=chapter.content,
                word_count=chapter.word_count,
            )
            for chapter in result.chapters
        ],
    )
