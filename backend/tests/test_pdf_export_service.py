"""
测试 PDF 导出服务
"""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import ValidationError
from app.schemas.projects import ProjectDetailResponse, ProjectSummaryResponse
from app.schemas.requests import ChapterInput
from app.schemas.responses import ValidationResponse
from app.services.pdf_export_service import export_project_pdf


def _make_mock_project(current_yaml: str) -> ProjectDetailResponse:
    return ProjectDetailResponse(
        id=1,
        title="测试项目",
        genre="都市",
        chapter_count=3,
        generation_mode="mock",
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
        source_content="测试内容",
        chapters=[ChapterInput(id="C001", title="第一章", content="内容", word_count=2)],
        current_yaml=current_yaml,
        validation=ValidationResponse(valid=True, errors=[]),
    )


SAMPLE_YAML = """
script:
  title: 测试剧本
  genre: 都市
  version: "1.0.0"
  source:
    chapter_count: 1
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
      location: 咖啡馆
      time: 白天
      source_chapters:
        - C001
      characters:
        - CHAR001
      beats:
        - type: narration
          text: 阳光洒进咖啡馆
        - type: dialogue
          character: CHAR001
          text: 你好
  adaptation_notes: []
  open_questions: []
"""


@patch("app.services.pdf_export_service.SimpleDocTemplate")
@patch("app.services.pdf_export_service.BytesIO")
def test_pdf_export_returns_bytes(mock_bytesio, mock_doc_template):
    """PDF 导出返回字节数据"""
    mock_buffer = MagicMock()
    mock_buffer.getvalue.return_value = b"fake-pdf-bytes"
    mock_bytesio.return_value = mock_buffer

    mock_doc = MagicMock()
    mock_doc_template.return_value = mock_doc

    project = _make_mock_project(SAMPLE_YAML)
    result = export_project_pdf(project)

    assert result == b"fake-pdf-bytes"
    mock_doc.build.assert_called_once()


@patch("app.services.pdf_export_service.SimpleDocTemplate")
@patch("app.services.pdf_export_service.BytesIO")
def test_pdf_export_contains_cover_title(mock_bytesio, mock_doc_template):
    """PDF 导出包含剧本标题"""
    mock_buffer = MagicMock()
    mock_buffer.getvalue.return_value = b"fake-pdf-bytes"
    mock_bytesio.return_value = mock_buffer

    mock_doc = MagicMock()
    mock_doc_template.return_value = mock_doc

    project = _make_mock_project(SAMPLE_YAML)
    export_project_pdf(project)

    # 验证 build 被调用且有内容
    assert mock_doc.build.called
    story = mock_doc.build.call_args[0][0]
    # story 中至少有一个 Paragraph 包含标题
    titles = [s for s in story if hasattr(s, "text") and "测试剧本" in getattr(s, "text", "")]
    assert len(titles) > 0


def test_pdf_export_raises_on_invalid_yaml():
    """无效 YAML 抛出 ValidationError"""
    project = _make_mock_project("这不是 YAML: [")
    with pytest.raises(ValidationError, match="YAML 解析失败"):
        export_project_pdf(project)


def test_pdf_export_raises_missing_script():
    """缺少 script 字段抛出 ValidationError"""
    project = _make_mock_project("title: 无 script 字段")
    with pytest.raises(ValidationError, match="缺少 script"):
        export_project_pdf(project)


def test_pdf_export_handles_empty_characters_and_scenes():
    """空角色表和场景列表也能正常导出"""
    min_yaml = """
script:
  title: 空项目
  genre: 未分类
  version: "1.0.0"
  source:
    chapter_count: 0
  characters: []
  scenes: []
  adaptation_notes: []
  open_questions: []
"""
    with (
        patch("app.services.pdf_export_service.SimpleDocTemplate") as mock_cls,
        patch("app.services.pdf_export_service.BytesIO") as mock_bio,
    ):
        mock_bio_instance = MagicMock()
        mock_bio_instance.getvalue.return_value = b"pdf"
        mock_bio.return_value = mock_bio_instance

        mock_doc = MagicMock()
        mock_cls.return_value = mock_doc

        project = _make_mock_project(min_yaml)
        result = export_project_pdf(project)
        assert result == b"pdf"
