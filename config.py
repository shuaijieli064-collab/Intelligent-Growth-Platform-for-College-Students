"""Application configuration with external JSON overrides."""
from __future__ import annotations

import base64
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def _obscure(text: str) -> str:
    """Simple base64 encode to avoid plain-text API key in config file."""
    if not text:
        return ""
    return base64.b64encode(text.encode()).decode()


def _clarify(text: str) -> str:
    """Decode obscured API key."""
    if not text:
        return ""
    try:
        return base64.b64decode(text.encode()).decode()
    except Exception:
        return text  # fallback for legacy plain-text keys

# ============================================================
# 默认配置
# ============================================================
DEFAULT_DB_CONFIG = {
    "db_type": "mysql",  # "mysql" 或 "postgres"
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "lsjhappy123..",
    "database": "student_growth_platform",
    "charset": "utf8mb4",
}

DEFAULT_LLM_CONFIG = {
    "provider": "deepseek",
    "api_key": "",
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
}

# LLM 提供商预设
LLM_PROVIDERS: dict[str, dict[str, str]] = {
    "deepseek": {
        "name": "DeepSeek (推荐·免费)",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat",
        "register_url": "https://platform.deepseek.com/",
    },
    "zhipu": {
        "name": "智谱AI (GLM-4)",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "model": "glm-4-flash",
        "register_url": "https://open.bigmodel.cn/",
    },
    "qwen": {
        "name": "通义千问 (Qwen)",
        "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "model": "qwen-turbo",
        "register_url": "https://dashscope.console.aliyun.com/",
    },
    "custom": {
        "name": "自定义 (OpenAI兼容)",
        "api_url": "",
        "model": "",
        "register_url": "",
    },
}

# ============================================================
# 数字孪生 - 健康度权重配置
# ============================================================
HEALTH_WEIGHTS = {
    "academic": 0.35,
    "physical": 0.25,
    "mental": 0.25,
    "social": 0.15,
}

RISK_THRESHOLDS = {
    "low": 80,
    "medium": 60,
    "high": 40,
}

CONFIG_FILENAME = "config.json"
CONFIG_ENV_VAR = "TRAININGPROJECT_CONFIG"


def _module_dir() -> Path:
    return Path(__file__).resolve().parent


def _app_config_dir() -> Path:
    base = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / "TrainingProject"
    return Path.home() / ".trainingproject"


def _candidate_config_paths() -> list[Path]:
    paths = []
    if getattr(sys, "frozen", False):
        paths.append(Path(sys.executable).resolve().parent / CONFIG_FILENAME)
    paths.append(_module_dir() / CONFIG_FILENAME)
    env_path = os.environ.get(CONFIG_ENV_VAR)
    if env_path:
        paths.append(Path(env_path))
    paths.append(_app_config_dir() / CONFIG_FILENAME)
    return paths


def _merge_dict(default: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(default)
    for key, value in override.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_env_overrides(db_config: dict[str, Any], llm_config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """从环境变量读取配置覆盖（用于云部署，如 Render）.

    支持的环境变量：
      DB_TYPE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
      LLM_PROVIDER, LLM_API_KEY, LLM_API_URL, LLM_MODEL
      DATABASE_URL (Supabase/Render 自动注入的 Postgres 连接字符串)
    """
    # 优先解析 DATABASE_URL（云平台自动注入）
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # 格式: postgresql://user:password@host:port/dbname
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        db_config["db_type"] = "postgres"
        db_config["host"] = parsed.hostname or db_config["host"]
        db_config["port"] = parsed.port or 5432
        db_config["user"] = parsed.username or db_config["user"]
        db_config["password"] = parsed.password or db_config["password"]
        db_config["database"] = parsed.path.lstrip("/") or db_config["database"]

    # 单独环境变量覆盖
    if os.environ.get("DB_TYPE"):
        db_config["db_type"] = os.environ["DB_TYPE"].lower()
    if os.environ.get("DB_HOST"):
        db_config["host"] = os.environ["DB_HOST"]
    if os.environ.get("DB_PORT"):
        db_config["port"] = int(os.environ["DB_PORT"])
    if os.environ.get("DB_USER"):
        db_config["user"] = os.environ["DB_USER"]
    if os.environ.get("DB_PASSWORD"):
        db_config["password"] = os.environ["DB_PASSWORD"]
    if os.environ.get("DB_NAME"):
        db_config["database"] = os.environ["DB_NAME"]

    # LLM 环境变量
    if os.environ.get("LLM_PROVIDER"):
        llm_config["provider"] = os.environ["LLM_PROVIDER"]
    if os.environ.get("LLM_API_KEY"):
        llm_config["api_key"] = os.environ["LLM_API_KEY"]
    if os.environ.get("LLM_API_URL"):
        llm_config["api_url"] = os.environ["LLM_API_URL"]
    if os.environ.get("LLM_MODEL"):
        llm_config["model"] = os.environ["LLM_MODEL"]

    return db_config, llm_config


def load_runtime_config() -> tuple[dict[str, Any], dict[str, Any]]:
    db_config = deepcopy(DEFAULT_DB_CONFIG)
    llm_config = deepcopy(DEFAULT_LLM_CONFIG)

    # 1. 从 config.json 加载（桌面版主要方式）
    for config_path in _candidate_config_paths():
        if not config_path.exists():
            continue
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            db_section = raw.get("db_config")
            if isinstance(db_section, dict):
                db_config = _merge_dict(db_config, db_section)
            llm_section = raw.get("llm_config")
            if isinstance(llm_section, dict):
                llm_config = _merge_dict(llm_config, llm_section)
        break

    # 2. 环境变量覆盖（云部署主要方式，优先级最高）
    db_config, llm_config = _load_env_overrides(db_config, llm_config)

    # Decode obscured API key（仅当来自 config.json 的 base64 编码）
    if llm_config.get("api_key"):
        llm_config["api_key"] = _clarify(llm_config["api_key"])

    return db_config, llm_config


def save_runtime_config(
    db_config: dict[str, Any],
    llm_config: dict[str, Any] | None = None,
    config_path: Path | None = None,
) -> Path:
    target_path = config_path or (_module_dir() / CONFIG_FILENAME)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    llm_cfg = _merge_dict(DEFAULT_LLM_CONFIG, llm_config or {})
    # Encode API key before saving
    if llm_cfg.get("api_key"):
        llm_cfg["api_key"] = _obscure(llm_cfg["api_key"])
    payload = {
        "db_config": _merge_dict(DEFAULT_DB_CONFIG, db_config),
        "llm_config": llm_cfg,
    }
    with target_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return target_path


def save_llm_config_to_json(provider: str, api_key: str, api_url: str = "", model: str = "") -> Path:
    """保存 LLM 配置到 config.json（API Key 自动加密）. """
    llm_cfg = {"provider": provider, "api_key": api_key}
    if api_url:
        llm_cfg["api_url"] = api_url
    if model:
        llm_cfg["model"] = model
    return save_runtime_config(DEFAULT_DB_CONFIG, llm_cfg, _module_dir() / CONFIG_FILENAME)


def reload_llm_config() -> dict[str, Any]:
    """重新加载 LLM 配置（用于运行时更新后）. """
    global LLM_CONFIG
    _, LLM_CONFIG = load_runtime_config()
    return LLM_CONFIG


def config_file_exists() -> bool:
    return any(path.exists() for path in _candidate_config_paths())


DB_CONFIG, LLM_CONFIG = load_runtime_config()
