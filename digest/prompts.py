# -*- coding: utf-8 -*-
"""Тексти інструкцій для AI лежать у папці prompts/ — їх можна правити як звичайний документ."""
from .config import ROOT


def load(name: str) -> str:
    return (ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8").strip()


def render(template: str, **values) -> str:
    text = load(template)
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text
