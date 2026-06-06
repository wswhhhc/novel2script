from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_database
from app.routers import batch, chapters, projects, script

# 加载项目根目录的 .env 文件
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:15173",
    ],
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
