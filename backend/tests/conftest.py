import sys
import os
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("NOVEL2SCRIPT_DB_PATH", str(BACKEND_ROOT / ".pytest_cache" / "novel2script-test.db"))
