from fastapi import APIRouter

from app.schemas.requests import ParseChaptersRequest
from app.schemas.responses import ChapterResponse, ParseChaptersResponse
from app.services.chapter_parser import parse_chapters

router = APIRouter(prefix="/api/chapters", tags=["chapters"])


@router.post(
    "/parse",
    response_model=ParseChaptersResponse,
    summary="解析小说章节",
    description=(
        "从小说文本中智能识别章节标题和内容。\n\n"
        "**支持格式**：\n"
        "- 中文：`第一章 标题` / `第1章 标题`\n"
        "- 英文：`Chapter 1: Title` / `Chapter One: Title`\n"
        "- 数字：`1. 标题` / `01. 标题`\n"
        "- 符号：`【1】标题` / `（1）标题`\n\n"
        "**约束**：\n"
        "- 最少 3 章节\n"
        "- 最多 20 章节\n"
        "- 总字数不超过 50,000 字\n"
        "- 单章节超过 10,000 字会返回警告\n\n"
        "**返回**：章节列表（ID、标题、内容、字数）+ 校验结果 + 警告信息"
    ),
    responses={
        200: {
            "description": "识别成功",
            "content": {
                "application/json": {
                    "example": {
                        "chapter_count": 3,
                        "valid": True,
                        "message": "识别到 3 个章节",
                        "warnings": [],
                        "chapters": [{"id": "C001", "title": "序章", "content": "...", "word_count": 2500}],
                    }
                }
            },
        }
    },
)
def parse_chapters_endpoint(request: ParseChaptersRequest) -> ParseChaptersResponse:
    """解析小说章节，识别标题和内容"""
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
