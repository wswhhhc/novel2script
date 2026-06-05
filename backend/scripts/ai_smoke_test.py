"""
Manual smoke test for real AI generation.

Run only after setting ENABLE_AI_GENERATION=true and MODEL_API_KEY.
This script calls the model provider and may incur cost.
"""
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.config.settings import settings
from app.services.chapter_parser import parse_chapters
from app.services.script_generator import generate_script_with_ai


def main() -> None:
    if not settings.enable_ai_generation:
        raise SystemExit("ENABLE_AI_GENERATION is not true; refusing to run real AI smoke test.")
    if not settings.model_api_key:
        raise SystemExit("MODEL_API_KEY is empty; refusing to run real AI smoke test.")

    sample_path = settings.project_root / "examples" / "novel-sample-1.txt"
    parse_result = parse_chapters(sample_path.read_text(encoding="utf-8"))
    if not parse_result.valid:
        raise SystemExit(f"Sample chapter parse failed: {parse_result.message}")

    result = generate_script_with_ai("AI Smoke Test", "悬疑", parse_result.chapters)
    output_path = Path(__file__).resolve().parent / "ai-smoke-output.yaml"
    output_path.write_text(result.yaml, encoding="utf-8")

    print(f"AI smoke test validation.valid={result.validation.valid}")
    if result.validation.errors:
        print("Validation errors:")
        for error in result.validation.errors:
            print(f"- {error}")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
