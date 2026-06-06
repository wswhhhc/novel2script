import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    # 章节限制
    min_chapters: int = 3
    max_chapters: int = 20
    max_input_length: int = 50_000
    max_chapter_length: int = 10_000

    # 路径配置
    backend_root: Path = BACKEND_ROOT
    project_root: Path = PROJECT_ROOT
    schema_path: Path = project_root / "schemas" / "script.schema.json"
    sample_output_path: Path = project_root / "examples" / "script-output-1.yaml"
    prompts_dir: Path = project_root / "prompts"
    database_path: Path = Path(os.getenv("NOVEL2SCRIPT_DB_PATH", backend_root / "data" / "novel2script.db"))

    # AI 模型配置
    model_provider: str = os.getenv("MODEL_PROVIDER", "openai")
    model_name: str = os.getenv("MODEL_NAME", "")
    model_api_key: str = os.getenv("MODEL_API_KEY", "")
    model_base_url: str = os.getenv("MODEL_BASE_URL", "https://api.openai.com/v1")
    model_temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    model_max_tokens: int = int(os.getenv("MODEL_MAX_TOKENS", "4000"))
    model_timeout: int = int(os.getenv("MODEL_TIMEOUT", "120"))
    model_max_retries: int = int(os.getenv("MODEL_MAX_RETRIES", "2"))

    # 生成配置
    enable_ai_generation: bool = os.getenv("ENABLE_AI_GENERATION", "false").lower() == "true"
    auto_fix_attempts: int = int(os.getenv("AUTO_FIX_ATTEMPTS", "3"))


settings = Settings()
