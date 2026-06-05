import copy

import yaml

from app.config.settings import settings
from app.services.script_validator import validate_script_yaml


def test_sample_yaml_passes_validation():
    yaml_text = settings.sample_output_path.read_text(encoding="utf-8")

    result = validate_script_yaml(yaml_text)

    assert result.valid is True
    assert result.errors == []


def test_missing_required_field_fails_validation():
    yaml_text = settings.sample_output_path.read_text(encoding="utf-8")
    document = yaml.safe_load(yaml_text)
    document["script"].pop("genre")

    result = validate_script_yaml(yaml.safe_dump(document, allow_unicode=True))

    assert result.valid is False
    assert any("genre" in error for error in result.errors)


def test_missing_character_reference_fails_validation():
    yaml_text = settings.sample_output_path.read_text(encoding="utf-8")
    document = yaml.safe_load(yaml_text)
    broken_document = copy.deepcopy(document)
    broken_document["script"]["scenes"][0]["characters"].append("CHAR999")
    broken_document["script"]["scenes"][0]["beats"][2]["character"] = "CHAR999"

    result = validate_script_yaml(yaml.safe_dump(broken_document, allow_unicode=True))

    assert result.valid is False
    assert any("不存在的角色" in error for error in result.errors)


def test_chapter_count_mismatch_fails_validation():
    yaml_text = settings.sample_output_path.read_text(encoding="utf-8")
    document = yaml.safe_load(yaml_text)
    document["script"]["source"]["chapter_count"] = 4

    result = validate_script_yaml(yaml.safe_dump(document, allow_unicode=True))

    assert result.valid is False
    assert any("chapter_count" in error for error in result.errors)


def test_invalid_created_at_fails_validation():
    yaml_text = settings.sample_output_path.read_text(encoding="utf-8")
    document = yaml.safe_load(yaml_text)
    document["script"]["created_at"] = "not-a-date"

    result = validate_script_yaml(yaml.safe_dump(document, allow_unicode=True))

    assert result.valid is False
    assert any("date-time" in error for error in result.errors)
