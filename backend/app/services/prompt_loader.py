"""
Prompt 模板加载和变量替换服务。

模板使用 ``{variable}`` 或 ``{{variable}}`` 两种占位符格式。
dict/list 变量自动序列化为 JSON（缩进形式），便于在 Prompt 中展示结构化数据。
"""

import json
import re

from app.config.settings import settings

# 匹配单大括号占位符：{var_name}
_PLACEHOLDER_RE = re.compile(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})")


def load_prompt_template(prompt_file: str, **variables) -> str:
    """
    从 prompts/ 目录加载 Prompt 模板并替换变量。

    Args:
        prompt_file: Prompt 文件名，如 ``01_chapter_analysis.txt``。
        **variables: 要替换的变量键值对。dict/list 自动序列化为 JSON。

    Returns:
        替换变量后的 Prompt 文本。

    Raises:
        FileNotFoundError: Prompt 文件不存在。
        ValueError: 模板中使用了未提供的变量。
    """
    prompt_path = settings.prompts_dir / prompt_file
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt 文件不存在：{prompt_path}")

    template = prompt_path.read_text(encoding="utf-8")

    # 将 dict/list 自动序列化为 JSON，其余转 str
    formatted: dict[str, str] = {}
    for key, value in variables.items():
        formatted[key] = (
            json.dumps(value, ensure_ascii=False, indent=2) if isinstance(value, (dict, list)) else str(value)
        )

    # 第 1 步：规范化双大括号 {{var}} → {var}，统一处理
    rendered = re.sub(r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}", r"{\1}", template)

    # 第 2 步：检查是否所有占位符都有对应值
    found = set(_PLACEHOLDER_RE.findall(rendered))
    missing = sorted(found - formatted.keys())
    if missing:
        raise ValueError(f"Prompt 模板缺少变量：{', '.join(missing)}")

    # 第 3 步：单次替换全部 {var}
    for key, value in formatted.items():
        rendered = rendered.replace(f"{{{key}}}", value)

    # 第 4 步：反转义模板中 {{ 和 }} 形式的字面量（用于 JSON/YAML 示例）
    rendered = rendered.replace("{{", "{").replace("}}", "}")

    return rendered


def format_chapters_for_prompt(chapters: list) -> str:
    """
    将章节列表格式化为 Prompt 友好的纯文本。

    每章格式::

        [C001] 第一章标题
        正文内容

        [C002] 第二章标题
        正文内容

    Args:
        chapters: 章节列表，每项包含 id / title / content。

    Returns:
        格式化的章节文本。
    """
    lines: list[str] = []
    for chapter in chapters:
        lines.append(f"[{chapter['id']}] {chapter['title']}")
        lines.append(chapter["content"])
        lines.append("")  # 空行分隔
    return "\n".join(lines)
