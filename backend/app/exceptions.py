"""
自定义服务层异常。

这些异常在 FastAPI 路由层由全局 exception_handler 统一捕获
并映射为对应的 HTTP 状态码，避免服务层直接依赖 fastapi.HTTPException。
"""


class ServiceError(Exception):
    """服务层异常基类（默认映射 HTTP 500）。"""


class NotFoundError(ServiceError):
    """资源不存在（映射 HTTP 404）。"""


class ValidationError(ServiceError):
    """输入校验失败（映射 HTTP 400）。"""


class AIServiceUnavailable(ServiceError):
    """AI 服务调用失败（映射 HTTP 503）。"""
