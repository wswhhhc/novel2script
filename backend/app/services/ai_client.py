"""
AI 模型调用客户端。

默认自动化测试不应触发真实网络请求；只有 ENABLE_AI_GENERATION=true 且配置
MODEL_API_KEY 后才会调用模型。
"""

import json
import time
from collections.abc import Iterator
from enum import Enum
from typing import Any

from app.config.settings import settings


class AIClientError(Exception):
    """AI 客户端调用错误。"""


class ErrorCategory(Enum):
    """AI 调用错误分类，用于决定是否重试。"""

    AUTH = "auth"                # 认证失败 — 不应重试
    TIMEOUT = "timeout"          # 超时 — 可重试
    RATE_LIMIT = "rate_limit"    # 限流 — 可重试
    CONNECTION = "connection"    # 连接失败 — 可重试
    SERVER = "server"            # 服务端错误 — 可重试
    EMPTY = "empty"              # 返回为空 — 不应重试
    PARSE = "parse"              # 结构异常 — 不应重试
    UNKNOWN = "unknown"          # 未知错误 — 可重试

    @property
    def retryable(self) -> bool:
        return self in (ErrorCategory.TIMEOUT, ErrorCategory.RATE_LIMIT,
                        ErrorCategory.CONNECTION, ErrorCategory.SERVER, ErrorCategory.UNKNOWN)


class CircuitState(Enum):
    CLOSED = "closed"            # 正常运行
    OPEN = "open"                # 熔断开启，拒绝请求
    HALF_OPEN = "half_open"      # 半开，允许试探


class CircuitBreaker:
    """简单的内存熔断器，防止持续调用失败的 AI 服务。"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0

    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN and time.monotonic() - self._last_failure_time > self._recovery_timeout:
            self._state = CircuitState.HALF_OPEN
        return self._state

    def call(self, fn, *args, **kwargs):
        """在熔断保护下调用函数。"""
        if self.state == CircuitState.OPEN:
            raise AIClientError(
                f"AI 服务熔断中（连续 {self._failure_count} 次失败），"
                f"将在 {int(self._recovery_timeout - (time.monotonic() - self._last_failure_time))} 秒后自动恢复"
            )

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except AIClientError:
            self._on_failure()
            raise

    def _on_success(self):
        self._failure_count = 0
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED

    def _on_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN

    def reset(self):
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0


# 全局熔断器实例
_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)


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
                return _circuit_breaker.call(_do_call_openai, prompt)
            if provider == "anthropic":
                return _circuit_breaker.call(_do_call_anthropic, prompt)
            raise AIClientError(f"不支持的 AI 提供商：{provider}")
        except AIClientError as exc:
            last_error = exc
            category = _classify_error(exc)
            if not category.retryable or attempt >= retries:
                raise
            time.sleep(3 * (attempt + 1))

    raise last_error or AIClientError("AI 调用失败")


def stream_ai_model(prompt: str) -> Iterator[str]:
    """流式调用 AI 模型，逐块返回生成内容。"""
    if not settings.enable_ai_generation:
        raise AIClientError("AI 生成未启用。请设置 ENABLE_AI_GENERATION=true 后再调用真实模型")
    if not settings.model_api_key:
        raise AIClientError("AI 模式已启用，但未配置 MODEL_API_KEY")
    if not settings.model_name:
        raise AIClientError("AI 模式已启用，但未配置 MODEL_NAME")

    provider = settings.model_provider.lower().strip()
    if provider == "openai":
        yield from _circuit_breaker.call(_do_stream_openai, prompt)
    elif provider == "anthropic":
        yield from _circuit_breaker.call(_do_stream_anthropic, prompt)
    else:
        raise AIClientError(f"不支持的 AI 提供商：{provider}")


def _classify_error(error: AIClientError) -> ErrorCategory:
    """根据错误信息分类错误类型。"""
    msg = str(error)
    if "认证" in msg or "MODEL_API_KEY" in msg:
        return ErrorCategory.AUTH
    if "超时" in msg:
        return ErrorCategory.TIMEOUT
    if "限流" in msg or "429" in msg or "额度" in msg:
        return ErrorCategory.RATE_LIMIT
    if "连接失败" in msg:
        return ErrorCategory.CONNECTION
    if "服务端错误" in msg:
        return ErrorCategory.SERVER
    if "为空" in msg:
        return ErrorCategory.EMPTY
    if "结构异常" in msg or "解析失败" in msg:
        return ErrorCategory.PARSE
    return ErrorCategory.UNKNOWN


# ── OpenAI ────────────────────────────────────────────────────────────


def _build_openai_client():
    """延迟导入并构建 OpenAI 客户端。"""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise AIClientError("未安装 openai 包。请运行：pip install openai") from exc
    return OpenAI(
        api_key=settings.model_api_key,
        base_url=settings.model_base_url or None,
        timeout=settings.model_timeout,
    )


def _translate_openai_error(exc: Exception) -> AIClientError:
    """将 OpenAI SDK 异常映射为统一的 AIClientError。"""
    from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, RateLimitError

    if isinstance(exc, AuthenticationError):
        return AIClientError("OpenAI 兼容 API 认证失败，请检查 MODEL_API_KEY")
    if isinstance(exc, APITimeoutError):
        return AIClientError(f"OpenAI 兼容 API 调用超时（{settings.model_timeout}s）")
    if isinstance(exc, RateLimitError):
        return AIClientError("OpenAI 兼容 API 限流或额度不足（429）")
    if isinstance(exc, APIConnectionError):
        return AIClientError("OpenAI 兼容 API 连接失败，请检查 MODEL_BASE_URL 和网络")
    if isinstance(exc, APIError):
        status = getattr(exc, "status_code", "unknown")
        prefix = "服务端错误" if status is not None and int(status) >= 500 else "调用失败"
        return AIClientError(f"OpenAI 兼容 API {prefix}（{status}）")
    return AIClientError(f"OpenAI 兼容 API 调用失败：{exc}")


def _extract_openai_content(response) -> str:
    """从 OpenAI 非流式响应中提取文本内容。"""
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError) as exc:
        raise AIClientError("OpenAI 兼容 API 返回结构异常，未找到 choices[0].message.content") from exc
    if not content or not content.strip():
        raise AIClientError("OpenAI 兼容 API 返回内容为空")
    return content.strip()


def _do_call_openai(prompt: str) -> str:
    """调用 OpenAI 兼容 API（非流式）。"""
    client = _build_openai_client()
    try:
        response = client.chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.model_temperature,
            max_tokens=settings.model_max_tokens,
        )
    except Exception as exc:
        raise _translate_openai_error(exc) from exc
    return _extract_openai_content(response)


def _do_stream_openai(prompt: str) -> Iterator[str]:
    """调用 OpenAI 兼容 API（流式），逐 chunk 产出内容。"""
    client = _build_openai_client()
    try:
        stream = client.chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.model_temperature,
            max_tokens=settings.model_max_tokens,
            stream=True,
        )
    except Exception as exc:
        raise _translate_openai_error(exc) from exc

    try:
        yielded = False
        for chunk in stream:
            try:
                content = chunk.choices[0].delta.content
            except (AttributeError, IndexError):
                content = None
            if content:
                yielded = True
                yield content
        if not yielded:
            raise AIClientError("OpenAI 兼容 API 返回内容为空")
    except AIClientError:
        raise
    except Exception as exc:
        raise _translate_openai_error(exc) from exc


# ── Anthropic ─────────────────────────────────────────────────────────


def _build_anthropic_client():
    """延迟导入并构建 Anthropic 客户端。"""
    try:
        import anthropic
    except ImportError as exc:
        raise AIClientError("未安装 anthropic 包。请运行：pip install anthropic") from exc
    return anthropic.Anthropic(
        api_key=settings.model_api_key,
        timeout=settings.model_timeout,
    )


def _translate_anthropic_error(exc: Exception) -> AIClientError:
    """将 Anthropic SDK 异常映射为统一的 AIClientError。"""
    import anthropic

    if isinstance(exc, anthropic.AuthenticationError):
        return AIClientError("Anthropic API 认证失败，请检查 MODEL_API_KEY")
    if isinstance(exc, anthropic.APITimeoutError):
        return AIClientError(f"Anthropic API 调用超时（{settings.model_timeout}s）")
    if isinstance(exc, anthropic.RateLimitError):
        return AIClientError("Anthropic API 限流或额度不足（429）")
    if isinstance(exc, anthropic.APIConnectionError):
        return AIClientError("Anthropic API 连接失败，请检查网络")
    if isinstance(exc, anthropic.APIStatusError):
        status = getattr(exc, "status_code", None)
        if status is not None and int(status) >= 500:
            return AIClientError(f"Anthropic API 服务端错误（{status}）")
        return AIClientError(f"Anthropic API 调用失败（{status or 'unknown'}）")
    if isinstance(exc, anthropic.APIError):
        return AIClientError("Anthropic API 调用失败")
    return AIClientError(f"Anthropic API 调用失败：{exc}")


def _extract_anthropic_content(response) -> str:
    """从 Anthropic 非流式响应中提取文本内容。"""
    try:
        content = response.content[0].text
    except (AttributeError, IndexError) as exc:
        raise AIClientError("Anthropic API 返回结构异常，未找到 content[0].text") from exc
    if not content or not content.strip():
        raise AIClientError("Anthropic API 返回内容为空")
    return content.strip()


def _do_call_anthropic(prompt: str) -> str:
    """调用 Anthropic API（非流式）。"""
    client = _build_anthropic_client()
    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=settings.model_max_tokens,
            temperature=settings.model_temperature,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        raise _translate_anthropic_error(exc) from exc
    return _extract_anthropic_content(response)


def _do_stream_anthropic(prompt: str) -> Iterator[str]:
    """调用 Anthropic API（流式），逐 chunk 产出内容。"""
    client = _build_anthropic_client()
    yielded = False
    try:
        with client.messages.stream(
            model=settings.model_name,
            max_tokens=settings.model_max_tokens,
            temperature=settings.model_temperature,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for content in stream.text_stream:
                if content:
                    yielded = True
                    yield content
        if not yielded:
            raise AIClientError("Anthropic API 返回内容为空")
    except AIClientError:
        raise
    except Exception as exc:
        raise _translate_anthropic_error(exc) from exc


# ── 通用工具 ──────────────────────────────────────────────────────────


def parse_json_response(text: str, stage_name: str = "AI 阶段") -> Any:
    """
    从 AI 响应中解析 JSON，支持直接 JSON 和 Markdown 代码块包裹。

    Args:
        text: AI 返回的原始文本。
        stage_name: 阶段名称，用于错误信息。

    Returns:
        解析后的 Python 对象（通常是 dict 或 list）。
    """
    candidate = _extract_code_block(text, "json") or _extract_code_block(text, None) or text.strip()
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        snippet = _response_snippet(text)
        raise AIClientError(f"{stage_name} JSON 解析失败：{exc.msg}。响应片段：{snippet}") from exc


def _extract_code_block(text: str, language: str | None) -> str | None:
    """从 Markdown 文本中提取代码块内容。"""
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
    """截取响应前 N 字符用于错误信息（将空白压缩为单空格）。"""
    compact = " ".join(text.strip().split())
    return compact[:limit] + "..." if len(compact) > limit else compact
