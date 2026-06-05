import json

from app.config.settings import settings
from app.schemas.requests import ChapterInput
from app.services import script_generator


def _chapters() -> list[ChapterInput]:
    return [
        ChapterInput(id="C001", title="第一章", content="林昭进入客栈。", word_count=7),
        ChapterInput(id="C002", title="第二章", content="旧案卷宗缺页。", word_count=7),
        ChapterInput(id="C003", title="第三章", content="暗巷发现密信。", word_count=7),
    ]


def _json_response(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def test_generate_script_with_ai_runs_all_generation_stages(monkeypatch):
    sample_yaml = settings.sample_output_path.read_text(encoding="utf-8")
    prompts: list[str] = []
    responses = iter(
        [
            _json_response({"chapters_analysis": []}),
            _json_response({"characters": []}),
            _json_response({"scenes": []}),
            f"```yaml\n{sample_yaml}\n```",
        ]
    )

    def fake_call_ai_model(prompt: str) -> str:
        prompts.append(prompt)
        return next(responses)

    monkeypatch.setattr(script_generator, "call_ai_model", fake_call_ai_model)

    result = script_generator.generate_script_with_ai("测试小说", "悬疑", _chapters())

    assert result.validation.valid is True
    assert result.yaml.startswith("script:")
    assert len(prompts) == 4
    assert "小说标题：测试小说" in prompts[0]
    assert "{{" not in prompts[0]
    assert "}}" not in prompts[0]


def test_generate_script_with_ai_fixes_invalid_yaml(monkeypatch):
    sample_yaml = settings.sample_output_path.read_text(encoding="utf-8")
    prompts: list[str] = []
    responses = iter(
        [
            _json_response({"chapters_analysis": []}),
            _json_response({"characters": []}),
            _json_response({"scenes": []}),
            "script:\n  title: 缺少必填字段\n",
            sample_yaml,
        ]
    )

    def fake_call_ai_model(prompt: str) -> str:
        prompts.append(prompt)
        return next(responses)

    monkeypatch.setattr(script_generator, "call_ai_model", fake_call_ai_model)

    result = script_generator.generate_script_with_ai("测试小说", "悬疑", _chapters())

    assert result.validation.valid is True
    assert len(prompts) == 5
    assert "缺少必填字段" in prompts[-1]


def test_extract_yaml_supports_plain_and_markdown_blocks():
    sample_yaml = settings.sample_output_path.read_text(encoding="utf-8")

    assert script_generator._extract_yaml_from_response(sample_yaml).startswith("script:")
    assert script_generator._extract_yaml_from_response(f"```yaml\n{sample_yaml}\n```").startswith("script:")
    assert script_generator._extract_yaml_from_response(f"说明文字\n{sample_yaml}\n\n补充说明").startswith("script:")


def test_generate_script_with_ai_returns_invalid_when_fix_fails(monkeypatch):
    prompts: list[str] = []
    invalid_yaml = "script:\n  title: 缺少必填字段\n"
    responses = iter(
        [
            _json_response({"chapters_analysis": []}),
            _json_response({"characters": []}),
            _json_response({"scenes": []}),
            invalid_yaml,
            invalid_yaml,
            invalid_yaml,
            invalid_yaml,
        ]
    )

    def fake_call_ai_model(prompt: str) -> str:
        prompts.append(prompt)
        return next(responses)

    monkeypatch.setattr(script_generator, "call_ai_model", fake_call_ai_model)
    monkeypatch.setattr(settings, "auto_fix_attempts", 3)

    result = script_generator.generate_script_with_ai("测试小说", "悬疑", _chapters())

    assert result.validation.valid is False
    assert result.yaml.startswith("script:")
    assert "缺少必填字段" in result.yaml
    assert len(prompts) == 7
    assert result.validation.errors
