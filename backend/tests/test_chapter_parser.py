from app.services.chapter_parser import parse_chapters


def test_parse_standard_three_chapters_success():
    content = """
第一章 雨夜来客
林昭推门而入。

Chapter 2: Old Case
卷宗少了两页。

3. 暗巷追踪
沈月识破了火漆袋。
"""

    result = parse_chapters(content)

    assert result.valid is True
    assert result.chapter_count == 3
    assert [chapter.id for chapter in result.chapters] == ["C001", "C002", "C003"]
    assert result.chapters[0].title == "第一章 雨夜来客"
    assert result.chapters[0].word_count == len("林昭推门而入。")


def test_parse_less_than_three_chapters_invalid():
    content = """
第1章 开端
第一章内容。

第二章 发展
第二章内容。
"""

    result = parse_chapters(content)

    assert result.valid is False
    assert result.chapter_count == 2
    assert "章节数量不足" in result.message


def test_parse_without_chapter_markers_invalid():
    result = parse_chapters("这是一段没有章节标题的小说正文。")

    assert result.valid is False
    assert result.chapter_count == 0
    assert "无法自动识别章节格式" in result.message


def test_parse_long_chapter_returns_warning_but_remains_valid():
    content = f"""
第一章 开端
{"一" * 10001}

第二章 发展
第二章内容。

第三章 结尾
第三章内容。
"""

    result = parse_chapters(content)

    assert result.valid is True
    assert result.chapter_count == 3
    assert result.warnings
    assert "章节内容过长" in result.warnings[0]
