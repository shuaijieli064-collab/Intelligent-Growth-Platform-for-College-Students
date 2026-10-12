"""pytest 公共配置：在所有测试前初始化 DatabaseManager 单例."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from config import DB_CONFIG
from data_layer.database import DatabaseManager


@pytest.fixture(scope="session", autouse=True)
def _db_manager() -> DatabaseManager:
    """测试套件共享同一个数据库单例，避免 get_instance() 抛 RuntimeError."""
    if DatabaseManager._instance is not None:
        return DatabaseManager.get_instance()
    kwargs = {k: v for k, v in DB_CONFIG.items() if k != "db_type"}
    return DatabaseManager(**kwargs)
