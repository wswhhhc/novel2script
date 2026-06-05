from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app
from app.services.chapter_parser import parse_chapters


client = TestClient(app)


def _chapters_text(count: int, body_length: int) -> str:
    return "\n".join(
        f"第{index}章 测试章节{index}\n{'内' * body_length}"
        for index in range(1, count + 1)
    )


def test_tc008_input_near_limit_is_accepted():
    content = _chapters_text(20, 2450)

    assert len(content) <= settings.max_input_length
    result = parse_chapters(content)

    assert result.valid is True
    assert result.chapter_count == settings.max_chapters


def test_tc008_generate_accepts_content_near_limit():
    chapters = [
        {
            "id": f"C{index:03d}",
            "title": f"第{index}章",
            "content": "内" * 2400,
            "word_count": 2400,
        }
        for index in range(1, settings.max_chapters + 1)
    ]

    response = client.post(
        "/api/script/generate",
        json={"title": "边界输入", "genre": "悬疑", "chapters": chapters},
    )

    assert response.status_code == 200
    assert response.json()["validation"]["valid"] is True


def test_tc009_parse_rejects_input_over_total_limit():
    content = "第一章 超长\n" + ("内" * (settings.max_input_length + 1))

    result = parse_chapters(content)

    assert result.valid is False
    assert "输入文本过长" in result.message
    assert str(settings.max_input_length) in result.message


def test_tc009_generate_rejects_input_over_total_limit():
    chapters = [
        {"id": "C001", "title": "第一章", "content": "内" * 20_000, "word_count": 20_000},
        {"id": "C002", "title": "第二章", "content": "内" * 20_000, "word_count": 20_000},
        {"id": "C003", "title": "第三章", "content": "内" * 10_001, "word_count": 10_001},
    ]

    response = client.post(
        "/api/script/generate",
        json={"title": "超限输入", "genre": "悬疑", "chapters": chapters},
    )

    assert response.status_code == 400
    assert "输入文本过长" in response.json()["detail"]


def test_tc009_parse_rejects_more_than_max_chapters():
    result = parse_chapters(_chapters_text(settings.max_chapters + 1, 10))

    assert result.valid is False
    assert "章节数量过多" in result.message
    assert str(settings.max_chapters) in result.message
