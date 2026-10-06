# -*- coding: utf-8 -*-
"""Завантаження налаштувань: config.yaml (методика, ліміти) + .env (провайдер AI і ключ)."""
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path):
    """Мінімальний читач .env: KEY=VALUE, коментарі #. Змінні середовища мають пріоритет."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load(config_path: Path | None = None) -> dict:
    _load_dotenv(ROOT / ".env")
    cfg = yaml.safe_load((config_path or ROOT / "config.yaml").read_text(encoding="utf-8"))
    cfg["root"] = ROOT
    # напрям можна задати й просто назвою (без іконки) — тоді іконка «other»
    cfg["taxonomy"]["domains"] = {
        k: v if isinstance(v, dict) else {"name": v, "icon": "other"}
        for k, v in cfg["taxonomy"]["domains"].items()}
    cfg["llm"].update({
        "provider": os.environ.get("LLM_PROVIDER", "anthropic").strip().lower(),
        "api_key": os.environ.get("LLM_API_KEY", "").strip(),
        "model": os.environ.get("LLM_MODEL", "claude-haiku-4-5").strip(),
        "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip(),
        "azure_api_version": os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21").strip(),
    })
    return cfg


def path(cfg: dict, relative: str) -> Path:
    return cfg["root"] / relative
