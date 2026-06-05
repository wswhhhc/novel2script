"""
AI 模型调用客户端。

默认自动化测试不应触发真实网络请求；只有 ENABLE_AI_GENERATION=true 且配置
MODEL_API_KEY 后才会调用模型。
"""
import json
import time
from typing import Any

from app.config.settings import settings


class AIClientError(Exception):
    """AI 客户端调用错误。"""


def call_ai_model(prompt: str, max_retries: int | None = None) -> str:
    """
    调用 AI 模型生成内容。

    Args:
        prompt: 输入 Prompt 文本。
        max_retries: 最大重试次数；None 时读取 MODEL_MAX_RETRIES。

    Raises:
        AIClientError: 配置缺失、依赖缺失、模型调用失败或返回空内容。
    """
    if not settings.enable_ai_generation:
        raise AIClientError("AI 生成未启用。请设置 ENABLE_AI_GENERATION=true 后再调用真实模型")

    if not settings.model_api_key:
        raise AIClientError("AI 模式已启用，但未配置 MODEL_API_KEY")

    if not settings.model_name:
        raise AIClientError("AI 模式已启用，但未配置 MODEL_NAME")

    provider = settings.model_provider.lower().strip()
    retries = settings.model_max_retries if max_retries is None else max_retries
    last_error: AIClientError | None = None

    for attempt in range(retries + 1):
        try:
            if provider == "openai":
                return _call_openai(prompt)
            if provider == "anthropic":
                return _call_anthropic(prompt)
            raise AIClientError(f"不支持的 AI 提供商：{provider}")
        except AIClientError as exc:
            last_error = exc
            if not _should_retry_error(exc) or attempt >= retries:
                raise
            time.sleep(3 * (attempt + 1))

    raise last_error or AIClientError("AI 调用失败")


def _call_openai(prompt: str) -> str:
    try:
        from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError
    except ImportError as exc:
        raise AIClientError("未安装 openai 包。请运行：pip install openai") from exc

    client = OpenAI(
        api_key=settings.model_api_key,
        base_url=settings.model_base_url or None,
        timeout=settings.model_timeout,
    )

    try:
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.model_temperature,
            max_tokens=settings.model_max_tokens,
        )
    except AuthenticationError as exc:
        raise AIClientError("OpenAI 兼容 API 认证失败，请检查 MODEL_API_KEY") from exc
    except APITimeoutError as exc:
        raise AIClientError(f"OpenAI 兼容 API 调用超时（{settings.model_timeout}s）") from exc
    except RateLimitError as exc:
        raise AIClientError("OpenAI 兼容 API 限流或额度不足（429）") from exc
    except APIConnectionError as exc:
        raise AIClientError("OpenAI 兼容 API 连接失败，请检查 MODEL_BASE_URL 和网络") from exc
    except APIError as exc:
        status_code = getattr(exc, "status_code", None)
        if status_code and int(status_code) >= 500:
            raise AIClientError(f"OpenAI 兼容 API 服务端错误（{status_code}）") from exc
        raise AIClientError(f"OpenAI 兼容 API 调用失败（{status_code or 'unknown'}）") from exc

    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError) as exc:
        raise AIClientError("OpenAI 兼容 API 返回结构异常，未找到 choices[0].message.content") from exc

    if not content or not content.strip():
        raise AIClientError("OpenAI 兼容 API 返回内容为空")

    return content.strip()


def _call_anthropic(prompt: str) -> str:
    try:
        import anthropic
    except ImportError as exc:
        raise AIClientError("未安装 anthropic 包。请运行：pip install anthropic") from exc

    client = anthropic.Anthropic(api_key=settings.model_api_key, timeout=settings.model_timeout)

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=settings.model_max_tokens,
            temperature=settings.model_temperature,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError as exc:
        raise AIClientError("Anthropic API 认证失败，请检查 MODEL_API_KEY") from exc
    except anthropic.APITimeoutError as exc:
        raise AIClientError(f"Anthropic API 调用超时（{settings.model_timeout}s）") from exc
    except anthropic.RateLimitError as exc:
        raise AIClientError("Anthropic API 限流或额度不足（429）") from exc
    except anthropic.APIStatusError as exc:
        status_code = getattr(exc, "status_code", None)
        if status_code and int(status_code) >= 500:
            raise AIClientError(f"Anthropic API 服务端错误（{status_code}）") from exc
        raise AIClientError(f"Anthropic API 调用失败（{status_code or 'unknown'}）") from exc
    except anthropic.APIError as exc:
        raise AIClientError("Anthropic API 调用失败") from exc

    try:
        content = response.content[0].text
    except (AttributeError, IndexError) as exc:
        raise AIClientError("Anthropic API 返回结构异常，未找到 content[0].text") from exc

    if not content or not content.strip():
        raise AIClientError("Anthropic API 返回内容为空")

    return content.strip()


def parse_json_response(text: str, stage_name: str = "AI 阶段") -> Any:
    """
    从 AI 响应中解析 JSON，支持直接 JSON 和 Markdown 代码块。
    """
    candidate = _extract_code_block(text, "json") or _extract_code_block(text, None) or text.strip()

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        snippet = _response_snippet(text)
        raise AIClientError(f"{stage_name} JSON 解析失败：{exc.msg}。响应片段：{snippet}") from exc


def _extract_code_block(text: str, language: str | None) -> str | None:
    lower_text = text.lower()
    if language:
        marker = f"```{language}"
        start = lower_text.find(marker)
        if start == -1:
            return None
        content_start = text.find("\n", start)
        if content_start == -1:
            return None
        content_start += 1
    else:
        start = text.find("```")
        if start == -1:
            return None
        content_start = text.find("\n", start)
        if content_start == -1:
            content_start = start + 3
        else:
            content_start += 1

    end = text.find("```", content_start)
    if end == -1:
        return None
    return text[content_start:end].strip()


def _response_snippet(text: str, limit: int = 300) -> str:
    compact = " ".join(text.strip().split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "..."


def _should_retry_error(error: AIClientError) -> bool:
    message = str(error)
    retry_markers = ["超时", "限流", "429", "服务端错误", "连接失败"]
    return any(marker in message for marker in retry_markers)
