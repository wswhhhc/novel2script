"""
Prompt 模板加载和变量替换服务
"""

import json
import re

from app.config.settings import settings

PLACEHOLDER_RE = re.compile(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})|\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}")


def load_prompt_template(prompt_file: str, **variables) -> str:
    """
    从 prompts/ 目录加载 Prompt 模板并替换变量

    Args:
        prompt_file: Prompt 文件名，如 "01_chapter_analysis.txt"
        **variables: 要替换的变量，如 title="小说标题", genre="悬疑"

    Returns:
        替换变量后的 Prompt 文本

    Raises:
        FileNotFoundError: 如果 Prompt 文件不存在
    """
    prompt_path = settings.prompts_dir / prompt_file

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt 文件不存在：{prompt_path}")

    template = prompt_path.read_text(encoding="utf-8")

    formatted_variables: dict[str, str] = {}
    for key, value in variables.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        else:
            value = str(value)
        formatted_variables[key] = value

    missing_keys = sorted(
        {
            match.group(1) or match.group(2)
            for match in PLACEHOLDER_RE.finditer(template)
            if (match.group(1) or match.group(2)) not in formatted_variables
        }
    )
    if missing_keys:
        raise ValueError(f"Prompt 模板缺少变量：{', '.join(missing_keys)}")

    rendered = template
    for key, value in formatted_variables.items():
        rendered = rendered.replace("{{" + key + "}}", value)
        rendered = rendered.replace("{" + key + "}", value)

    # 兼容旧模板为 .format() 转义过的 JSON/YAML 示例。
    return rendered.replace("{{", "{").replace("}}", "}")


def format_chapters_for_prompt(chapters: list) -> str:
    """
    将章节列表格式化为 Prompt 友好的文本格式

    Args:
        chapters: 章节列表，每个章节包含 id, title, content

    Returns:
        格式化的章节文本
    """
    lines = []
    for chapter in chapters:
        lines.append(f"[{chapter['id']}] {chapter['title']}")
        lines.append(f"{chapter['content']}")
        lines.append("")  # 空行分隔

    return "\n".join(lines)
