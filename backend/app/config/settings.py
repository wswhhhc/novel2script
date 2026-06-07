import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "env_file_encoding": "utf-8", "extra": "ignore"}

    # 章节限制
    min_chapters: int = 3
    max_chapters: int = 20
    max_input_length: int = 50_000
    max_chapter_length: int = 10_000

    # 路径配置
    NOVEL2SCRIPT_DB_PATH: str = str(BACKEND_ROOT / "data" / "novel2script.db")
    GENERATION_CACHE_DIR: str = str(BACKEND_ROOT / "data" / "generation_cache")

    # AI 模型配置
    model_provider: str = "openai"
    model_name: str = ""
    model_api_key: str = ""
    model_base_url: str = "https://api.openai.com/v1"
    model_temperature: float = 0.7
    model_max_tokens: int = 4000
    model_timeout: int = 120
    model_max_retries: int = 2

    # CORS 配置（逗号分隔的字符串，通过 property 转为 list）
    CORS_ORIGINS: str = "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:15173,http://120.53.0.252"

    # 生成配置
    enable_ai_generation: bool = False
    enable_generation_cache: bool = True
    auto_fix_attempts: int = 3

    # 路径（衍生属性）
    backend_root: Path = BACKEND_ROOT
    project_root: Path = PROJECT_ROOT

    # 测试用的私有覆盖字段（允许 monkeypatch）
    _prompts_dir_override: Path | None = None
    _generation_cache_dir_override: Path | None = None
    _schema_path_override: Path | None = None
    _sample_output_path_override: Path | None = None

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def database_path(self) -> Path:
        return Path(self.NOVEL2SCRIPT_DB_PATH)

    @property
    def schema_path(self) -> Path:
        return self._schema_path_override or self.project_root / "schemas" / "script.schema.json"

    @schema_path.setter
    def schema_path(self, value: Path) -> None:
        self._schema_path_override = value

    @property
    def sample_output_path(self) -> Path:
        return self._sample_output_path_override or self.project_root / "examples" / "script-output-1.yaml"

    @sample_output_path.setter
    def sample_output_path(self, value: Path) -> None:
        self._sample_output_path_override = value

    @property
    def prompts_dir(self) -> Path:
        return self._prompts_dir_override or self.project_root / "prompts"

    @prompts_dir.setter
    def prompts_dir(self, value: Path) -> None:
        self._prompts_dir_override = value

    @property
    def generation_cache_dir(self) -> Path:
        return self._generation_cache_dir_override or Path(os.getenv("GENERATION_CACHE_DIR", self.GENERATION_CACHE_DIR))

    @generation_cache_dir.setter
    def generation_cache_dir(self, value: Path) -> None:
        self._generation_cache_dir_override = value


settings = Settings()
