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


def load_runtime_config() -> tuple[dict[str, Any], dict[str, Any]]:
    db_config = deepcopy(DEFAULT_DB_CONFIG)
    llm_config = deepcopy(DEFAULT_LLM_CONFIG)

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

    # Decode obscured API key
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
