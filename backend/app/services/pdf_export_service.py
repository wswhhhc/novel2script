"""
PDF 导出服务
将 YAML 剧本导出为专业格式的 PDF
"""

import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Any

import yaml
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.exceptions import ValidationError
from app.schemas.projects import ProjectDetailResponse

logger = logging.getLogger(__name__)

# ── 中文字体配置（延迟注册，字体缺失时降级为 Helvetica）────────────────
_CN_FONT = "Helvetica"  # 降级默认值
_CN_FONT_READY = False


def _register_cn_font() -> None:
    """尝试注册中文字体。失败时不报错，保持 Helvetica 降级。"""
    global _CN_FONT, _CN_FONT_READY

    ttf_path = os.getenv(
        "CN_TTF_PATH",
        "/usr/share/texlive/texmf-dist/fonts/truetype/public/arphic-ttf/gbsn00lp.ttf",
    )
    p = Path(ttf_path)
    if not p.exists():
        logger.warning("中文字体文件 %s 不存在，PDF 中文可能无法正常显示", ttf_path)
        return

    font_name = "ARPL-SungtiL-GB"
    try:
        pdfmetrics.registerFont(TTFont(font_name, str(p)))
        addMapping(font_name, 0, 0, font_name)
        addMapping(font_name, 1, 0, font_name)
        addMapping(font_name, 0, 1, font_name)
        addMapping(font_name, 1, 1, font_name)
        _CN_FONT = font_name
        _CN_FONT_READY = True
        logger.info("已注册中文字体：%s", ttf_path)
    except Exception as exc:
        logger.warning("注册中文字体失败：%s，PDF 中文可能无法正常显示", exc)


def export_project_pdf(project: ProjectDetailResponse) -> bytes:
    """
    导出项目为 PDF 格式

    Args:
        project: 项目详细信息

    Returns:
        PDF 字节数据

    Raises:
        HTTPException: YAML 解析失败时
    """
    try:
        script_data = yaml.safe_load(project.current_yaml)
    except yaml.YAMLError as exc:
        raise ValidationError(f"YAML 解析失败，无法导出 PDF：{exc}") from exc

    if not isinstance(script_data, dict) or "script" not in script_data:
        raise ValidationError("YAML 格式错误：缺少 script 顶层字段")

    script = script_data["script"]

    # 懒加载中文字体（仅在首次导出时尝试注册，失败降级不崩溃）
    if not _CN_FONT_READY:
        _register_cn_font()

    buffer = BytesIO()

    # 创建 PDF 文档
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # 构建内容
    story = []
    styles = getSampleStyleSheet()

    # 自定义样式
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName=_CN_FONT,
        fontSize=24,
        textColor=colors.HexColor("#1a202c"),
        spaceAfter=30,
        alignment=1,  # 居中
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName=_CN_FONT,
        fontSize=16,
        textColor=colors.HexColor("#2d3748"),
        spaceAfter=12,
        spaceBefore=20,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName=_CN_FONT,
        fontSize=11,
        leading=16,
    )

    dialogue_style = ParagraphStyle(
        "Dialogue",
        parent=styles["BodyText"],
        fontName=_CN_FONT,
        fontSize=11,
        leftIndent=20,
        spaceAfter=6,
    )

    # 封面
    story.append(Spacer(1, 2 * inch))
    story.append(Paragraph(_safe_str(script.get("title", "无标题")), title_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"类型：{_safe_str(script.get('genre', '未分类'))}", body_style))
    story.append(Paragraph(f"版本：{_safe_str(script.get('version', '1.0.0'))}", body_style))

    source = script.get("source", {})
    if isinstance(source, dict):
        chapter_count = source.get("chapter_count", 0)
        story.append(Paragraph(f"原著章节数：{chapter_count}", body_style))

    story.append(PageBreak())

    # 角色表
    characters = script.get("characters", [])
    if characters and isinstance(characters, list):
        story.append(Paragraph("角色表", heading_style))
        story.append(Spacer(1, 0.2 * inch))

        char_data = [["ID", "姓名", "角色", "首次出现"]]
        for char in characters:
            if isinstance(char, dict):
                char_data.append(
                    [
                        _safe_str(char.get("id", "")),
                        _safe_str(char.get("name", "")),
                        _safe_str(char.get("role", "")),
                        _safe_str(char.get("first_appearance", "")),
                    ]
                )

        char_table = Table(char_data, colWidths=[1.2 * inch, 1.5 * inch, 2 * inch, 1.3 * inch])
        char_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a202c")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), _CN_FONT),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e0")),
                ]
            )
        )
        story.append(char_table)
        story.append(PageBreak())

    # 场景列表
    scenes = script.get("scenes", [])
    if scenes and isinstance(scenes, list):
        story.append(Paragraph("场景列表", heading_style))
        story.append(Spacer(1, 0.2 * inch))

        for scene in scenes:
            if not isinstance(scene, dict):
                continue

            scene_title = f"{_safe_str(scene.get('id', ''))} - {_safe_str(scene.get('title', '未命名场景'))}"
            story.append(Paragraph(scene_title, heading_style))

            # 场景信息
            info_lines = [
                f"地点：{_safe_str(scene.get('location', '未指定'))}",
                f"时间：{_safe_str(scene.get('time', '未指定'))}",
                f"出场角色：{', '.join(_safe_list(scene.get('characters', [])))}",
                f"目的：{_safe_str(scene.get('purpose', ''))}",
            ]

            for line in info_lines:
                story.append(Paragraph(line, body_style))

            story.append(Spacer(1, 0.1 * inch))

            # 剧情节拍
            beats = scene.get("beats", [])
            if isinstance(beats, list):
                for beat in beats:
                    if not isinstance(beat, dict):
                        continue

                    beat_type = beat.get("type", "note")
                    beat_text = _safe_str(beat.get("text", ""))

                    if beat_type == "dialogue":
                        character = _safe_str(beat.get("character", ""))
                        emotion = beat.get("emotion")
                        emotion_tag = f"（{emotion}）" if emotion else ""
                        beat_content = f"<b>{character}{emotion_tag}：</b>{beat_text}"
                        story.append(Paragraph(beat_content, dialogue_style))
                    elif beat_type == "action":
                        story.append(Paragraph(f"<i>[动作] {beat_text}</i>", body_style))
                    elif beat_type == "narration":
                        story.append(Paragraph(f"<i>{beat_text}</i>", body_style))
                    elif beat_type == "transition":
                        story.append(Paragraph(f"<b>{beat_text}</b>", body_style))
                    else:
                        story.append(Paragraph(f"[{beat_type}] {beat_text}", body_style))

                    story.append(Spacer(1, 0.05 * inch))

            story.append(Spacer(1, 0.3 * inch))

    # 构建 PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


def _safe_str(value: Any) -> str:
    """安全转换为字符串"""
    if value is None:
        return ""
    return str(value).strip()


def _safe_list(value: Any) -> list[str]:
    """安全转换为字符串列表"""
    if not isinstance(value, list):
        return []
    return [_safe_str(item) for item in value if item is not None]
