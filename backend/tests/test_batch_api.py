"""
测试批量操作 API
"""
import pytest


def test_batch_delete_projects(test_client):
    """测试批量删除项目"""
    # 先创建3个项目
    project_ids = []
    for i in range(3):
        response = test_client.post(
            "/api/projects",
            json={
                "title": f"批量测试项目{i+1}",
                "genre": "都市",
                "source_content": "第一章 开始\n第二章 发展\n第三章 结局",
                "current_yaml": "script:\n  title: 测试",
                "chapter_count": 3,
            },
        )
        assert response.status_code == 200
        project_ids.append(response.json()["id"])

    # 批量删除前2个项目
    response = test_client.post("/api/batch/delete", json={"project_ids": project_ids[:2]})

    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 2
    assert len(data["failed_ids"]) == 0

    # 验证项目已删除
    for pid in project_ids[:2]:
        response = test_client.get(f"/api/projects/{pid}")
        assert response.status_code == 404

    # 第3个项目应该还存在
    response = test_client.get(f"/api/projects/{project_ids[2]}")
    assert response.status_code == 200


def test_batch_delete_with_invalid_ids(test_client):
    """测试删除不存在的项目"""
    response = test_client.post("/api/batch/delete", json={"project_ids": [9999, 9998]})

    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 0
    assert len(data["failed_ids"]) == 2
    assert len(data["errors"]) == 2


def test_batch_delete_exceeds_limit(test_client):
    """测试超出批量删除限制"""
    project_ids = list(range(1, 52))  # 51个项目
    response = test_client.post("/api/batch/delete", json={"project_ids": project_ids})

    assert response.status_code == 400
    assert "最多支持 50 个项目" in response.json()["detail"]


def test_batch_validate_projects(test_client):
    """测试批量校验项目"""
    # 创建一个有效项目
    valid_yaml = """script:
  title: 测试剧本
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
  scenes:
    - id: S001
      title: 开场
      source_chapters: [C001]
      location: 咖啡馆
      time: 白天
      characters: [CHAR001]
      purpose: 介绍主角
      beats:
        - type: action
          text: 张三走进咖啡馆
  adaptation_notes: []
  open_questions: []
"""

    response = test_client.post(
        "/api/projects",
        json={
            "title": "有效项目",
            "genre": "都市",
            "source_content": "第一章\n第二章\n第三章",
            "current_yaml": valid_yaml,
            "chapter_count": 3,
        },
    )
    assert response.status_code == 200
    valid_id = response.json()["id"]

    # 创建一个无效项目
    invalid_yaml = "script:\n  title: 缺少必填字段"

    response = test_client.post(
        "/api/projects",
        json={
            "title": "无效项目",
            "genre": "悬疑",
            "source_content": "第一章\n第二章\n第三章",
            "current_yaml": invalid_yaml,
            "chapter_count": 3,
        },
    )
    assert response.status_code == 200
    invalid_id = response.json()["id"]

    # 批量校验
    response = test_client.post("/api/batch/validate", json={"project_ids": [valid_id, invalid_id]})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["valid_count"] == 1
    assert data["invalid_count"] == 1
    assert len(data["results"]) == 2


def test_batch_stats(test_client):
    """测试获取批量统计信息"""
    # 创建几个测试项目
    for i in range(3):
        test_client.post(
            "/api/projects",
            json={
                "title": f"统计测试{i+1}",
                "genre": "都市" if i < 2 else "悬疑",
                "source_content": "第一章\n第二章\n第三章",
                "current_yaml": "script:\n  title: 测试",
                "chapter_count": 3,
            },
        )

    response = test_client.get("/api/batch/stats")

    assert response.status_code == 200
    data = response.json()
    assert "total_count" in data
    assert "avg_chapters" in data
    assert "genre_distribution" in data
    assert "mode_distribution" in data
    assert "recent_projects" in data
    assert data["total_count"] >= 3
