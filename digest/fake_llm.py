# -*- coding: utf-8 -*-
"""Імітація AI для перевірки конвеєра без ключа і без витрат (python run.py --dry-run).
Відповіді детерміновані й примітивні — це перевірка «чи все з'єднано», а не якості."""
import re

from .llm import Usage

KEYWORDS = ("price", "port", "oil", "soy", "grain", "tariff", "ship", "freight", "feed", "gas", "ціни", "порт")


class FakeLLM:
    provider = "dry-run"
    model = "dry-run"

    def __init__(self, cfg: dict):
        self.usage = Usage()
        tax = cfg["taxonomy"]
        self.domains = list(tax["domains"].keys())
        self.categories = list(tax["categories"])

    def json(self, system, prompt, max_tokens, schema=None, attempts=3, label=""):
        self.usage.add(len(prompt) // 4, 50)
        props = (schema or {}).get("properties", {})
        numbered = [b for b in re.split(r"\n(?=\d+\. )", prompt) if re.match(r"\d+\. ", b)]
        if prompt.startswith("Оціни кожну з"):  # 2-й етап класифікації — масив, як у старій версії
            out = []
            for i, b in enumerate(numbered):
                m = re.search(r"Заголовок: (.*)", b)
                title = m.group(1) if m else b
                out.append({"id": i, "score": 6, "domain": self.domains[i % 3], "reason_uk": "тест",
                            "category": self.categories[i % 3], "country": "", "commodity": "",
                            "summary_short": " ".join(title.split()[:8]), "summary_detailed": title})
            return out
        if prompt.startswith("Оціни "):  # 1-й етап: лише оцінки
            return [{"id": i, "score": 6 if any(k in b.lower() for k in KEYWORDS) else 3} for i, b in enumerate(numbered)]
        if "items" in props:  # переклад для конкурентів
            items = []
            for i, b in enumerate(numbered):
                m = re.search(r"Заголовок: (.*)", b)
                items.append({"id": i, "title_uk": (m.group(1) if m else b)[:200], "summary_uk": ""})
            return {"items": items}
        if "verdict" in props:
            refs = [int(x) for x in re.findall(r"^\[(\d+)\]", prompt, re.M)]
            return {"verdict": "Тестова довідка (dry-run)", "why": [],
                    "facts": [{"text": "Тестовий факт без чисел", "refs": refs[:1]}],
                    "events": [{"text": "Тестова подія", "refs": refs[:2], "type": "Тест", "confidence": "mid", "key": True}],
                    "related": [], "badge": {"text": "Тест", "tone": "neutral"}, "no_news": False}
        if "highlights" in prompt:
            return {"highlights": ["Тестова теза (dry-run)"]}
        return {"trend": "flat", "headline": "Тестовий підсумок (dry-run)", "bullets": [], "events": [], "no_news": True}
