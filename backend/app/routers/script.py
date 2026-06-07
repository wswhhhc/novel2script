import json
from collections.abc import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.config.settings import settings
from app.schemas.requests import GenerateScriptRequest, ValidateScriptRequest
from app.schemas.responses import GenerateScriptResponse, ValidationResponse
from app.services.script_generator import (
    generate_script_mock,
    generate_script_stream_events,
    generate_script_with_ai,
    validate_script_generation_input,
)
from app.services.script_validator import validate_script_yaml

router = APIRouter(prefix="/api/script", tags=["script"])


@router.get(
    "/mode",
    summary="获取生成模式",
    description=(
        "返回当前系统的生成模式配置，用于前端展示和配置排查。\n\n"
        "**Mock 模式**：返回预制示例剧本，无需 API Key，适合演示\n"
        "**AI 模式**：调用真实 AI 模型生成，需配置环境变量"
    ),
    responses={
        200: {
            "description": "配置信息",
            "content": {
                "application/json": {
                    "example": {
                        "mode": "mock",
                        "ai_enabled": False,
                        "provider": "openai",
                        "model": "",
                        "base_url_configured": False,
                        "api_key_configured": False,
                        "auto_fix_attempts": 3,
                    }
                }
            },
        }
    },
)
def generation_mode_endpoint() -> dict[str, object]:
    """获取当前生成模式配置"""
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


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="校验 YAML 剧本",
    description=(
        "对 YAML 剧本进行完整性校验。\n\n"
        "**校验内容**：\n"
        "- YAML 语法正确性\n"
        "- JSON Schema 结构约束（332 行规则）\n"
        "- 业务规则：ID 唯一性、引用完整性、字段一致性\n\n"
        "**常见错误**：\n"
        "- 缺少必填字段（如 `title`, `characters`）\n"
        "- ID 格式错误（必须符合 C001-C999 / CHAR001-CHAR999 / S001-S999）\n"
        "- 引用无效（如角色的 `first_appearance` 引用不存在的章节 ID）\n"
        "- 对话未指定角色（`dialogue` 类型 beat 必须有 `character` 字段）"
    ),
    responses={
        200: {
            "description": "校验结果",
            "content": {
                "application/json": {
                    "examples": {
                        "valid": {"summary": "校验通过", "value": {"valid": True, "errors": []}},
                        "invalid": {
                            "summary": "校验失败",
                            "value": {
                                "valid": False,
                                "errors": [
                                    "script.characters[0].first_appearance: 引用了不存在的章节 C999",
                                    "script.scenes[0].beats[0]: dialogue 类型必须包含 character 字段",
                                ],
                            },
                        },
                    }
                }
            },
        }
    },
)
def validate_script_endpoint(request: ValidateScriptRequest) -> ValidationResponse:
    """校验 YAML 剧本是否符合 Schema 和业务规则"""
    return validate_script_yaml(request.yaml)


@router.post(
    "/generate/stream",
    summary="流式生成剧本",
    description=(
        "根据小说章节生成结构化剧本，并以 NDJSON 逐行返回进度和 YAML 片段。\n\n"
        "事件格式：`status` 表示阶段进度，`yaml_delta` 表示新增 YAML 文本，"
        "`validation` 表示校验结果，`done` 表示完整结果。"
    ),
    responses={
        200: {
            "description": "流式生成事件",
            "content": {
                "application/x-ndjson": {
                    "example": '{"type":"status","message":"阶段 4/5：正在流式生成 YAML 剧本..."}\n'
                    '{"type":"yaml_delta","delta":"script:\\n  title: 示例"}\n'
                    '{"type":"done","yaml":"script:\\n  title: 示例","validation":{"valid":true,"errors":[]}}\n'
                }
            },
        },
        400: {"description": "输入验证失败（章节数不足、格式错误等）"},
    },
)
def generate_script_stream_endpoint(request: GenerateScriptRequest) -> StreamingResponse:
    """流式生成剧本，供前端边生成边展示"""
    validate_script_generation_input(request.title, request.genre, request.chapters)
    return StreamingResponse(
        _iter_stream_events(request),
        media_type="application/x-ndjson; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post(
    "/generate",
    response_model=GenerateScriptResponse,
    summary="生成剧本",
    description=(
        "根据小说章节生成结构化剧本。\n\n"
        "**生成模式**（由环境变量 `ENABLE_AI_GENERATION` 控制）：\n\n"
        "**Mock 模式**（默认）：\n"
        "- 返回预制的示例剧本 YAML\n"
        "- 不调用 AI，不消耗 API 额度\n"
        "- 适合演示、测试、前后端联调\n\n"
        "**AI 模式**（需配置）：\n"
        "- 五阶段生成链路：\n"
        "  1. 📊 章节分析：提取结构化信息（人物、事件、转折）\n"
        "  2. 👥 角色提取：跨章节统一角色，自动去重\n"
        "  3. 🎬 场景规划：拆分场景大纲，标注时空\n"
        "  4. 📝 剧本生成：生成完整 YAML 剧本\n"
        "  5. 🔧 自动修复：Schema 校验失败时自动修复（最多 3 次）\n\n"
        "**性能**：\n"
        "- Mock 模式：约 40ms\n"
        "- AI 模式：45-60s（3 章节，DeepSeek-V3 模型）\n\n"
        "**成本**：\n"
        "- Mock 模式：免费\n"
        "- AI 模式：约 ¥0.02-0.05/次（DeepSeek-V3）"
    ),
    responses={
        200: {
            "description": "生成成功",
            "content": {
                "application/json": {
                    "example": {
                        "yaml": "script:\n  title: 示例剧本\n  ...",
                        "validation": {"valid": True, "errors": []},
                    }
                }
            },
        },
        400: {"description": "输入验证失败（章节数不足、格式错误等）"},
        503: {"description": "AI 服务调用失败"},
    },
)
def generate_script_endpoint(request: GenerateScriptRequest) -> GenerateScriptResponse:
    """生成剧本（自动选择 Mock 或 AI 模式）"""
    if settings.enable_ai_generation:
        return generate_script_with_ai(request.title, request.genre, request.chapters)
    else:
        return generate_script_mock(request.title, request.genre, request.chapters)


def _iter_stream_events(request: GenerateScriptRequest) -> Iterator[str]:
    for event in generate_script_stream_events(request.title, request.genre, request.chapters):
        yield json.dumps(event, ensure_ascii=False) + "\n"
