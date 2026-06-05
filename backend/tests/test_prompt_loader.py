import pytest

from app.config.settings import settings
from app.services.prompt_loader import load_prompt_template


def test_all_prompt_templates_load_with_safe_variables():
    prompts = [
        (
            "01_chapter_analysis.txt",
            {"title": "测试小说", "genre": "悬疑", "chapters": "[C001] 第一章\n正文"},
        ),
        (
            "02_character_extraction.txt",
            {"title": "测试小说", "genre": "悬疑", "chapters_analysis": {"chapters_analysis": []}},
        ),
        (
            "03_scene_planning.txt",
            {
                "title": "测试小说",
                "genre": "悬疑",
                "chapters_analysis": {"chapters_analysis": []},
                "characters": {"characters": []},
            },
        ),
        (
            "04_script_generation.txt",
            {
                "title": "测试小说",
                "genre": "悬疑",
                "chapters": "[C001] 第一章\n正文",
                "chapters_analysis": {"chapters_analysis": []},
                "characters": {"characters": []},
                "scenes_outline": {"scenes": []},
            },
        ),
        (
            "05_yaml_fix.txt",
            {
                "original_yaml": "script:\n  title: 测试",
                "validation_errors": "1. 缺少字段",
                "schema_content": {"type": "object"},
            },
        ),
    ]

    for prompt_file, variables in prompts:
        prompt = load_prompt_template(prompt_file, **variables)
        assert "测试小说" in prompt or prompt_file == "05_yaml_fix.txt"
        assert "{{" not in prompt
        assert "}}" not in prompt


def test_prompt_template_formats_escaped_json_examples():
    prompt = load_prompt_template(
        "02_character_extraction.txt",
        title="测试小说",
        genre="悬疑",
        chapters_analysis={"chapters_analysis": []},
    )

    assert "小说标题：测试小说" in prompt
    assert '"chapters_analysis": []' in prompt
    assert "{{" not in prompt
    assert "}}" not in prompt


def test_prompt_template_reports_missing_variable(monkeypatch, tmp_path):
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    (prompts_dir / "broken.txt").write_text("小说标题：{title}\n缺失：{missing}", encoding="utf-8")
    monkeypatch.setattr(settings, "prompts_dir", prompts_dir)

    with pytest.raises(ValueError, match="missing"):
        load_prompt_template("broken.txt", title="测试小说")
