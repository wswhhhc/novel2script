from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app
from app.services.chapter_parser import parse_chapters
from app.services.script_validator import validate_script_yaml

client = TestClient(app)


def _read_example(name: str) -> str:
    return (settings.project_root / "examples" / name).read_text(encoding="utf-8")


def test_tc001_standard_sample_parses_generates_and_validates():
    content = _read_example("novel-sample-1.txt")

    parse_response = client.post("/api/chapters/parse", json={"content": content})

    assert parse_response.status_code == 200
    parse_data = parse_response.json()
    assert parse_data["valid"] is True
    assert parse_data["chapter_count"] >= 3

    generate_response = client.post(
        "/api/script/generate",
        json={"title": "雨中的重逢", "genre": "都市", "chapters": parse_data["chapters"]},
    )

    assert generate_response.status_code == 200
    generate_data = generate_response.json()
    assert generate_data["yaml"].startswith("script:")
    assert generate_data["validation"]["valid"] is True

    validation_response = client.post("/api/script/validate", json={"yaml": generate_data["yaml"]})
    assert validation_response.status_code == 200
    assert validation_response.json()["valid"] is True


def test_sample_two_and_three_are_parseable_for_demo():
    for sample_name in ["novel-sample-2.txt", "novel-sample-3.txt"]:
        result = parse_chapters(_read_example(sample_name))

        assert result.valid is True
        assert result.chapter_count >= settings.min_chapters
        assert [chapter.id for chapter in result.chapters] == [
            f"C{index:03d}" for index in range(1, result.chapter_count + 1)
        ]


def test_invalid_yaml_fixtures_fail_with_readable_errors():
    missing_required = validate_script_yaml(_read_example("invalid-script-missing-required.yaml"))
    bad_reference = validate_script_yaml(_read_example("invalid-script-bad-reference.yaml"))

    assert missing_required.valid is False
    assert any("genre" in error for error in missing_required.errors)
    assert bad_reference.valid is False
    assert any("不存在的角色" in error for error in bad_reference.errors)
    assert any("不存在的章节" in error for error in bad_reference.errors)
