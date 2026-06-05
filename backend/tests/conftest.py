import sys
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("NOVEL2SCRIPT_DB_PATH", str(BACKEND_ROOT / ".pytest_cache" / "novel2script-test.db"))


@pytest.fixture
def test_client():
    """创建测试客户端"""
    from app.main import app
    from app.db.database import init_database

    # 初始化测试数据库
    init_database()

    with TestClient(app) as client:
        yield client
