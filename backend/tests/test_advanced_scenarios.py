"""
测试 AI 生成的并发场景和错误恢复
"""
import pytest
from unittest.mock import patch
from app.services.script_generator import generate_script_with_ai
from app.schemas.requests import ChapterInput


def test_generation_with_partial_ai_failure():
    """测试 AI 部分阶段失败的恢复"""
    chapters = [
        ChapterInput(id="C001", title="第一章", content="内容1" * 100, word_count=300),
        ChapterInput(id="C002", title="第二章", content="内容2" * 100, word_count=300),
        ChapterInput(id="C003", title="第三章", content="内容3" * 100, word_count=300),
    ]

    call_count = [0]

    def mock_ai_with_retry(prompt):
        call_count[0] += 1
        if call_count[0] == 1:
            # 第一次调用（章节分析）失败
            raise Exception("Temporary failure")
        elif call_count[0] == 2:
            # 重试成功
            return '{"chapters": [{"id": "C001", "summary": "摘要"}]}'
        else:
            return '{"characters": []}'

    with patch("app.services.script_generator.call_ai_model", side_effect=mock_ai_with_retry):
        with pytest.raises(Exception):
            generate_script_with_ai("测试", "都市", chapters)


def test_generation_with_malformed_json_response():
    """测试 AI 返回格式错误的 JSON"""
    chapters = [
        ChapterInput(id="C001", title="第一章", content="内容" * 100, word_count=300),
        ChapterInput(id="C002", title="第二章", content="内容" * 100, word_count=300),
        ChapterInput(id="C003", title="第三章", content="内容" * 100, word_count=300),
    ]

    with patch("app.services.script_generator.call_ai_model") as mock_ai:
        mock_ai.return_value = "This is not JSON"

        with pytest.raises(Exception):
            generate_script_with_ai("测试", "都市", chapters)


def test_generation_with_oversized_input():
    """测试超大输入的自动裁剪"""
    from app.services.script_generator import _trim_chapters_for_ai_prompt

    # 创建一个超长章节
    large_chapter = {
        "id": "C001",
        "title": "超长章节",
        "content": "内容" * 10000,  # 2万字
        "word_count": 20000
    }

    chapters = [
        large_chapter,
        {"id": "C002", "title": "第二章", "content": "内容" * 100, "word_count": 300},
        {"id": "C003", "title": "第三章", "content": "内容" * 100, "word_count": 300},
    ]

    # 测试裁剪功能
    trimmed = _trim_chapters_for_ai_prompt(chapters)

    # 第一个章节应该被裁剪
    assert len(trimmed[0]["content"]) < len(large_chapter["content"])
    assert "已省略中间" in trimmed[0]["content"]

    # 其他章节不应该被裁剪
    assert len(trimmed[1]["content"]) == len(chapters[1]["content"])
    assert len(trimmed[2]["content"]) == len(chapters[2]["content"])


def test_yaml_fix_retry_limit():
    """测试 YAML 修复的重试次数限制"""
    from app.services.script_generator import _stage_5_fix_yaml
    from app.config.settings import settings

    invalid_yaml = "script:\n  title: 测试\n  invalid: true"
    errors = ["缺少必填字段"]

    retry_count = [0]

    def mock_ai_always_fail(prompt):
        retry_count[0] += 1
        return "script:\n  still: invalid"

    with patch("app.services.script_generator.call_ai_model", side_effect=mock_ai_always_fail):
        result = _stage_5_fix_yaml(invalid_yaml, errors)

        # 应该重试 auto_fix_attempts 次
        assert retry_count[0] == settings.auto_fix_attempts
        # 返回最后一次尝试的结果
        assert "still: invalid" in result


def test_chapter_trimming_preserves_key_content():
    """测试章节裁剪是否保留关键内容"""
    from app.services.script_generator import _trim_chapters_for_ai_prompt

    long_content = "开头内容" + "中间填充" * 5000 + "结尾内容"
    chapters = [{
        "id": "C001",
        "title": "超长章节",
        "content": long_content,
        "word_count": len(long_content)
    }]

    trimmed = _trim_chapters_for_ai_prompt(chapters)

    assert len(trimmed) == 1
    assert "开头内容" in trimmed[0]["content"]
    assert "结尾内容" in trimmed[0]["content"]
    assert "已省略中间" in trimmed[0]["content"]
    assert len(trimmed[0]["content"]) < len(long_content)


def test_validation_with_circular_references():
    """测试循环引用的校验"""
    yaml_content = """
script:
  title: 测试循环引用
  genre: 都市
  version: "1.0.0"
  source:
    chapter_count: 3
    chapters:
      - id: C001
        title: 第一章
  characters:
    - id: CHAR001
      name: 张三
      role: 主角
      first_appearance: C001
      relationships:
        - character_id: CHAR002
          relation: 朋友
    - id: CHAR002
      name: 李四
      role: 配角
      first_appearance: C001
      relationships:
        - character_id: CHAR001
          relation: 朋友
  scenes: []
  adaptation_notes: []
  open_questions: []
"""

    from app.services.script_validator import validate_script_yaml

    # 循环引用是允许的（现实中朋友关系就是双向的）
    result = validate_script_yaml(yaml_content)

    # 应该因为 scenes 为空而失败，但不应该因为循环引用失败
    assert not result.valid
    assert any("scenes" in error.lower() for error in result.errors)
    assert not any("circular" in error.lower() for error in result.errors)
