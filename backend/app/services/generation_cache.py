import hashlib
import json
from pathlib import Path
from typing import Any

from app.config.settings import settings


def get_cached_stage(stage: str, prompt: str) -> dict[str, Any] | None:
    if not settings.enable_generation_cache:
        return None

    path = _cache_path(stage, prompt)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def set_cached_stage(stage: str, prompt: str, payload: dict[str, Any]) -> None:
    if not settings.enable_generation_cache:
        return

    path = _cache_path(stage, prompt)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    temp_path.replace(path)


def _cache_path(stage: str, prompt: str) -> Path:
    digest_payload = {
        "stage": stage,
        "provider": settings.model_provider,
        "model": settings.model_name,
        "temperature": settings.model_temperature,
        "prompt": prompt,
    }
    digest = hashlib.sha256(json.dumps(digest_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    return settings.generation_cache_dir / stage / f"{digest}.json"
