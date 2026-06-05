from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app
from app.services.chapter_parser import parse_chapters


client = TestClient(app)


def _read_example(name: str) -> str:
    return (settings.project_root / "examples" / name).read_text(encoding="utf-8")


def test_tc002_too_few_chapters_returns_clear_message():
    response = client.post(
        "/api/chapters/parse",
        json={"content": _read_example("novel-edge-too-few-chapters.txt")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["chapter_count"] == 2
    assert "章节数量不足" in data["message"]


def test_tc003_unrecognized_text_returns_clear_message():
    response = client.post(
        "/api/chapters/parse",
        json={"content": "夜色沉下来，主角一路向前，没有任何章节标题或明显分隔。"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["chapter_count"] == 0
    assert "无法自动识别章节格式" in data["message"]


def test_tc004_long_chapter_returns_warning_without_blocking_generation():
    content = f"""
第一章 开端
{'内' * (settings.max_chapter_length + 1)}

第二章 发展
第二章内容。

第三章 结尾
第三章内容。
"""

    parse_response = client.post("/api/chapters/parse", json={"content": content})

    assert parse_response.status_code == 200
    parse_data = parse_response.json()
    assert parse_data["valid"] is True
    assert parse_data["warnings"]
    assert "章节内容过长" in parse_data["warnings"][0]

    generate_response = client.post(
        "/api/script/generate",
        json={"title": "长章节示例", "genre": "悬疑", "chapters": parse_data["chapters"]},
    )
    assert generate_response.status_code == 200


def test_tc005_mixed_chapter_formats_increment_ids():
    result = parse_chapters(_read_example("novel-edge-mixed-chapter-formats.txt"))

    assert result.valid is True
    assert result.chapter_count == 4
    assert [chapter.id for chapter in result.chapters] == ["C001", "C002", "C003", "C004"]
    assert result.chapters[1].title.startswith("Chapter 2")
    assert result.chapters[3].title.startswith("卷一 第四章")


def test_tc007_validate_endpoint_reports_fixture_errors():
    for fixture_name in ["invalid-script-missing-required.yaml", "invalid-script-bad-reference.yaml"]:
        response = client.post(
            "/api/script/validate",
            json={"yaml": _read_example(fixture_name)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert data["errors"]
