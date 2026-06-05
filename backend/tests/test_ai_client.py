import pytest

from app.config.settings import settings
from app.services.ai_client import AIClientError, call_ai_model, parse_json_response


def test_parse_json_response_supports_plain_json():
    parsed = parse_json_response('{"ok": true}', stage_name="测试阶段")

    assert parsed == {"ok": True}


def test_parse_json_response_supports_markdown_json_block():
    parsed = parse_json_response('说明\n```json\n{"ok": true}\n```', stage_name="测试阶段")

    assert parsed == {"ok": True}


def test_parse_json_response_reports_stage_and_snippet():
    with pytest.raises(AIClientError, match="测试阶段 JSON 解析失败"):
        parse_json_response("不是 JSON", stage_name="测试阶段")


def test_ai_client_does_not_call_network_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "enable_ai_generation", False)
    monkeypatch.setattr(settings, "model_api_key", "")

    with pytest.raises(AIClientError, match="AI 生成未启用"):
        call_ai_model("prompt")


def test_ai_client_reports_missing_api_key_without_network(monkeypatch):
    monkeypatch.setattr(settings, "enable_ai_generation", True)
    monkeypatch.setattr(settings, "model_api_key", "")

    with pytest.raises(AIClientError, match="MODEL_API_KEY"):
        call_ai_model("prompt")


def test_ai_client_reports_missing_model_name_without_network(monkeypatch):
    monkeypatch.setattr(settings, "enable_ai_generation", True)
    monkeypatch.setattr(settings, "model_api_key", "test-key")
    monkeypatch.setattr(settings, "model_name", "")

    with pytest.raises(AIClientError, match="MODEL_NAME"):
        call_ai_model("prompt")
