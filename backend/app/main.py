from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config.settings import settings
from app.db.database import init_database
from app.exceptions import AIServiceUnavailable, NotFoundError, ServiceError, ValidationError
from app.routers import batch, chapters, projects, script

# 加载项目根目录的 .env 文件
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    enabled=settings.enable_rate_limiting,
)

app = FastAPI(
    title="Novel2Script API",
    description=(
        "AI 驱动的智能小说剧本转换系统 API\n\n"
        "**核心功能**：\n"
        "- 📖 智能章节识别（支持 8+ 种中英文格式）\n"
        "- 🤖 五阶段 AI 生成链路（章节分析 → 角色提取 → 场景规划 → 剧本生成 → 自动修复）\n"
        "- ✅ 结构化 Schema 校验（332 行 JSON Schema 约束）\n"
        "- 💾 项目管理与版本快照\n"
        "- 📦 多格式导出（YAML / JSON / Markdown）\n\n"
        "**使用模式**：\n"
        "- Mock 模式：返回示例剧本，无需 API Key，适合演示和测试\n"
        "- AI 模式：调用真实 AI 模型生成，需配置环境变量\n\n"
        "详细文档见：https://github.com/wswhhhc/novel2script"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Novel2Script Team",
        "url": "https://github.com/wswhhhc/novel2script",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)
init_database()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(ServiceError)
def handle_service_error(request, exc: ServiceError) -> JSONResponse:
    """将服务层自定义异常映射为对应的 HTTP 状态码。"""
    status_map: dict[type[ServiceError], int] = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ValidationError: status.HTTP_400_BAD_REQUEST,
        AIServiceUnavailable: status.HTTP_503_SERVICE_UNAVAILABLE,
    }
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    for exc_type, http_code in status_map.items():
        if isinstance(exc, exc_type):
            code = http_code
            break
    return JSONResponse(status_code=code, content={"detail": str(exc)})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chapters.router)
app.include_router(script.router)
app.include_router(projects.router)
app.include_router(batch.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "novel2script-backend"}
