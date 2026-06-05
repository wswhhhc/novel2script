from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "novel2script-backend"}


def test_parse_chapters_endpoint():
    response = client.post(
        "/api/chapters/parse",
        json={"content": """
第一章 雨夜来客
正文一。
二、旧案
正文二。
卷一 第三章 暗巷追踪
正文三。
"""},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["chapter_count"] == 3


def test_validate_script_endpoint():
    yaml_text = settings.sample_output_path.read_text(encoding="utf-8")
    response = client.post("/api/script/validate", json={"yaml": yaml_text})

    assert response.status_code == 200
    assert response.json()["valid"] is True


def test_generate_script_mock_endpoint():
    chapters = [
        {"id": "C001", "title": "第一章", "content": "正文一", "word_count": 3},
        {"id": "C002", "title": "第二章", "content": "正文二", "word_count": 3},
        {"id": "C003", "title": "第三章", "content": "正文三", "word_count": 3},
    ]

    response = client.post(
        "/api/script/generate",
        json={"title": "测试小说", "genre": "悬疑", "chapters": chapters},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["yaml"].startswith("script:")
    assert data["validation"]["valid"] is True


def test_generation_mode_endpoint_defaults_to_mock():
    response = client.get("/api/script/mode")

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] in {"mock", "ai"}
    assert "api_key_configured" in data


def test_generate_script_ai_mode_missing_api_key_returns_clear_error(monkeypatch):
    monkeypatch.setattr(settings, "enable_ai_generation", True)
    monkeypatch.setattr(settings, "model_api_key", "")
    chapters = [
        {"id": "C001", "title": "第一章", "content": "正文一", "word_count": 3},
        {"id": "C002", "title": "第二章", "content": "正文二", "word_count": 3},
        {"id": "C003", "title": "第三章", "content": "正文三", "word_count": 3},
    ]

    response = client.post(
        "/api/script/generate",
        json={"title": "测试小说", "genre": "悬疑", "chapters": chapters},
    )

    assert response.status_code == 503
    assert "MODEL_API_KEY" in response.json()["detail"]


def test_generate_script_rejects_too_many_chapters():
    chapters = [
        {"id": f"C{index:03d}", "title": f"第{index}章", "content": "正文", "word_count": 2} for index in range(1, 22)
    ]

    response = client.post(
        "/api/script/generate",
        json={"title": "测试小说", "genre": "悬疑", "chapters": chapters},
    )

    assert response.status_code == 400
    assert "章节数量过多" in response.json()["detail"]


def test_generate_script_rejects_invalid_chapter_id():
    chapters = [
        {"id": "C001", "title": "第一章", "content": "正文一", "word_count": 3},
        {"id": "C002", "title": "第二章", "content": "正文二", "word_count": 3},
        {"id": "chapter-3", "title": "第三章", "content": "正文三", "word_count": 3},
    ]

    response = client.post(
        "/api/script/generate",
        json={"title": "测试小说", "genre": "悬疑", "chapters": chapters},
    )

    assert response.status_code == 400
    assert "章节 ID 格式错误" in response.json()["detail"]
