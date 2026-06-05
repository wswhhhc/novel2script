from fastapi import APIRouter

from app.config.settings import settings
from app.schemas.requests import GenerateScriptRequest, ValidateScriptRequest
from app.schemas.responses import GenerateScriptResponse, ValidationResponse
from app.services.script_generator import generate_script_mock, generate_script_with_ai
from app.services.script_validator import validate_script_yaml

router = APIRouter(prefix="/api/script", tags=["script"])


@router.get("/mode")
def generation_mode_endpoint() -> dict[str, object]:
    """返回当前生成模式，供前端展示和排查配置使用。"""
    provider = settings.model_provider.lower()
    return {
        "mode": "ai" if settings.enable_ai_generation else "mock",
        "ai_enabled": settings.enable_ai_generation,
        "provider": provider,
        "model": settings.model_name if settings.enable_ai_generation else "",
        "base_url_configured": bool(settings.model_base_url),
        "api_key_configured": bool(settings.model_api_key),
        "auto_fix_attempts": settings.auto_fix_attempts,
    }


@router.post("/validate", response_model=ValidationResponse)
def validate_script_endpoint(request: ValidateScriptRequest) -> ValidationResponse:
    """
    校验 YAML 剧本是否符合 Schema

    校验内容：
    - YAML 语法
    - JSON Schema 约束
    - 业务规则（ID 唯一性、引用合法性等）
    """
    return validate_script_yaml(request.yaml)


@router.post("/generate", response_model=GenerateScriptResponse)
def generate_script_endpoint(request: GenerateScriptRequest) -> GenerateScriptResponse:
    """
    生成剧本

    根据配置自动选择：
    - Mock 模式：返回示例 YAML（默认，用于前后端联调）
    - AI 模式：调用真实 AI 生成（需要配置 ENABLE_AI_GENERATION=true）

    AI 生成流程：
    1. 章节分析：提取摘要、人物、事件、地点
    2. 角色提取：生成统一角色表
    3. 场景规划：拆分场景并生成场景大纲
    4. 剧本生成：生成完整 YAML 剧本
    5. YAML 修复：如果校验失败，自动修复（最多 3 次）
    """
    if settings.enable_ai_generation:
        return generate_script_with_ai(request.title, request.genre, request.chapters)
    else:
        return generate_script_mock(request.title, request.genre, request.chapters)
