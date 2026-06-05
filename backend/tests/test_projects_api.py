from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app

client = TestClient(app)

CHAPTERS = [
    {"id": "C001", "title": "第一章", "content": "正文一", "word_count": 3},
    {"id": "C002", "title": "第二章", "content": "正文二", "word_count": 3},
    {"id": "C003", "title": "第三章", "content": "正文三", "word_count": 3},
]


def _sample_yaml() -> str:
    return settings.sample_output_path.read_text(encoding="utf-8")


def _create_project(title: str = "Phase6 测试项目", yaml_text: str | None = None) -> int:
    response = client.post(
        "/api/projects",
        json={
            "title": title,
            "genre": "悬疑",
            "source_content": "第一章 正文一\n第二章 正文二\n第三章 正文三",
            "chapters": CHAPTERS,
            "yaml": yaml_text or _sample_yaml(),
            "validation": {"valid": True, "errors": []},
            "generation_mode": "mock",
        },
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_create_project_success():
    project_id = _create_project("Phase6 创建项目")

    response = client.get(f"/api/projects/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Phase6 创建项目"
    assert data["chapter_count"] == 3
    assert data["current_yaml"].startswith("script:")
    assert data["validation"]["valid"] is True


def test_project_list_returns_created_project():
    project_id = _create_project("Phase6 项目列表")

    response = client.get("/api/projects")

    assert response.status_code == 200
    assert any(project["id"] == project_id for project in response.json())


def test_project_detail_contains_yaml_and_chapters():
    project_id = _create_project("Phase6 项目详情")

    response = client.get(f"/api/projects/{project_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["source_content"]
    assert len(data["chapters"]) == 3
    assert data["current_yaml"].startswith("script:")


def test_update_project_success():
    project_id = _create_project("Phase6 更新前")

    response = client.put(
        f"/api/projects/{project_id}",
        json={"title": "Phase6 更新后", "genre": "都市", "yaml": _sample_yaml()},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Phase6 更新后"
    assert data["genre"] == "都市"
    assert data["validation"]["valid"] is True


def test_delete_project_then_detail_returns_404():
    project_id = _create_project("Phase6 删除项目")

    delete_response = client.delete(f"/api/projects/{project_id}")
    detail_response = client.get(f"/api/projects/{project_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == project_id
    assert detail_response.status_code == 404


def test_create_and_list_versions():
    project_id = _create_project("Phase6 版本列表")

    response = client.post(
        f"/api/projects/{project_id}/versions",
        json={
            "version_name": "初稿 v1",
            "yaml": _sample_yaml(),
            "validation": {"valid": True, "errors": []},
            "note": "初稿",
        },
    )
    list_response = client.get(f"/api/projects/{project_id}/versions")

    assert response.status_code == 200
    assert response.json()["version_name"] == "初稿 v1"
    assert list_response.status_code == 200
    assert any(version["id"] == response.json()["id"] for version in list_response.json())


def test_version_detail_and_restore_updates_current_yaml():
    project_id = _create_project("Phase6 恢复版本")
    original_yaml = _sample_yaml()
    changed_yaml = original_yaml.replace("长夜初逢", "版本恢复标题", 1)
    version_response = client.post(
        f"/api/projects/{project_id}/versions",
        json={
            "version_name": "恢复目标",
            "yaml": changed_yaml,
            "validation": {"valid": True, "errors": []},
            "note": "",
        },
    )
    version_id = version_response.json()["id"]

    detail_response = client.get(f"/api/projects/{project_id}/versions/{version_id}")
    restore_response = client.post(f"/api/projects/{project_id}/versions/{version_id}/restore")

    assert detail_response.status_code == 200
    assert "版本恢复标题" in detail_response.json()["yaml"]
    assert restore_response.status_code == 200
    assert restore_response.json()["restored_from_version"] == version_id
    assert "版本恢复标题" in restore_response.json()["current_yaml"]


def test_export_yaml_returns_original_yaml():
    yaml_text = _sample_yaml()
    project_id = _create_project("Phase6 导出 YAML", yaml_text)

    response = client.get(f"/api/projects/{project_id}/export/yaml")

    assert response.status_code == 200
    assert response.text == yaml_text
    assert "Phase6_" in response.headers["content-disposition"]


def test_export_json_returns_parseable_json():
    project_id = _create_project("Phase6 导出 JSON")

    response = client.get(f"/api/projects/{project_id}/export/json")

    assert response.status_code == 200
    assert response.json()["script"]["title"]


def test_export_markdown_contains_title_characters_and_scenes():
    project_id = _create_project("Phase6 导出 Markdown")

    response = client.get(f"/api/projects/{project_id}/export/markdown")

    assert response.status_code == 200
    text = response.text
    assert "# " in text
    assert "## 角色表" in text
    assert "## 场景列表" in text


def test_invalid_project_id_returns_404():
    response = client.get("/api/projects/99999999")

    assert response.status_code == 404


def test_invalid_yaml_export_json_returns_clear_error():
    project_id = _create_project("Phase6 无效 YAML", "script:\n  title: [")

    response = client.get(f"/api/projects/{project_id}/export/json")

    assert response.status_code == 400
    assert "YAML 无法解析" in response.json()["detail"]
