import re
from dataclasses import dataclass

from app.config.settings import settings


@dataclass
class ParsedChapter:
    id: str
    title: str
    content: str
    word_count: int


@dataclass
class ChapterParseResult:
    chapter_count: int
    valid: bool
    message: str
    chapters: list[ParsedChapter]
    warnings: list[str]


CHAPTER_TITLE_RE = re.compile(
    r"(?im)^[ \t]*(?:卷\s*[0-9一二三四五六七八九十百千万]+[ \t　]+)?"
    r"("
    r"第\s*[0-9一二三四五六七八九十百千万]+\s*章(?:[ \t　:：.\-]+[^\r\n]*)?"
    r"|Chapter\s+(?:[0-9]+|[A-Za-z]+)(?:\s*[:：.\-]\s*[^\r\n]*)?"
    r"|[0-9]+[.、][ \t　]*[^\r\n]*"
    r"|[一二三四五六七八九十百千万]+[.、][ \t　]*[^\r\n]*"
    r")\s*$"
)


def parse_chapters(content: str) -> ChapterParseResult:
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) > settings.max_input_length:
        return ChapterParseResult(
            chapter_count=0,
            valid=False,
            message=f"输入文本过长（{len(text)} 字），超出上限 {settings.max_input_length} 字，请精简内容",
            chapters=[],
            warnings=[],
        )

    matches = list(CHAPTER_TITLE_RE.finditer(text))
    if not matches:
        # 当前仅支持正则识别。如需支持无标准格式的混合排版，
        # 可考虑增加 AI 辅助识别（调用 ai_client）或前端手动标注功能。
        return ChapterParseResult(
            chapter_count=0,
            valid=False,
            message="无法自动识别章节格式，请检查章节标题格式或使用手动标注",
            chapters=[],
            warnings=[],
        )

    chapters: list[ParsedChapter] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        title = match.group(0).strip()
        chapters.append(
            ParsedChapter(
                id=f"C{index + 1:03d}",
                title=title,
                content=body,
                word_count=len(body),
            )
        )

    empty_chapters = [chapter.id for chapter in chapters if not chapter.content]
    if empty_chapters:
        return ChapterParseResult(
            chapter_count=len(chapters),
            valid=False,
            message=f"章节内容为空，请检查输入内容：{', '.join(empty_chapters)}",
            chapters=chapters,
            warnings=[],
        )

    if len(chapters) < settings.min_chapters:
        return ChapterParseResult(
            chapter_count=len(chapters),
            valid=False,
            message=f"章节数量不足，需要至少 {settings.min_chapters} 个章节，当前识别到 {len(chapters)} 个章节",
            chapters=chapters,
            warnings=[],
        )

    if len(chapters) > settings.max_chapters:
        return ChapterParseResult(
            chapter_count=len(chapters),
            valid=False,
            message=f"章节数量过多，最多支持 {settings.max_chapters} 个章节，当前识别到 {len(chapters)} 个章节",
            chapters=chapters,
            warnings=[],
        )

    long_chapters = [
        f"{chapter.id}（{chapter.word_count} 字）"
        for chapter in chapters
        if chapter.word_count > settings.max_chapter_length
    ]
    if long_chapters:
        return ChapterParseResult(
            chapter_count=len(chapters),
            valid=True,
            message="章节识别成功，但存在章节内容过长，建议拆分或可能影响生成质量",
            chapters=chapters,
            warnings=[f"章节内容过长：{', '.join(long_chapters)}"],
        )

    return ChapterParseResult(
        chapter_count=len(chapters),
        valid=True,
        message="章节识别成功",
        chapters=chapters,
        warnings=[],
    )
