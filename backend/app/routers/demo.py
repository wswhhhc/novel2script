"""
演示数据接口。
提供一个缓存友好的接口，返回演示小说文本供前端一键填充。
"""

from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.get("/info")
def demo_info() -> dict:
    """返回演示小说数据（标题 + 类型 + 正文）。"""
    sample_path = settings.project_root / "examples" / "novel-sample-1.txt"
    content = sample_path.read_text(encoding="utf-8")
    return {
        "title": "暮色之约",
        "genre": "都市",
        "content": content.strip(),
    }
