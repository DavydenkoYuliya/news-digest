# -*- coding: utf-8 -*-
"""Автоматичні перевірки. Запуск:  python -m unittest discover tests
Працюють без ключа AI і без інтернету (AI імітується, новини — з tests/fixtures)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from digest import competitor_brief, competitors, dedup, guardrails, rss  # noqa: E402
from digest.category_briefs import _validate  # noqa: E402
import run  # noqa: E402


class GuardrailsTest(unittest.TestCase):
    def test_digit_groups(self):
        self.assertEqual(guardrails.digit_groups("4,12 млрд і 9.13%"), {"4", "12", "9", "13"})

    def test_numbers_must_come_from_source(self):
        src = [{"title_original": "Soymeal premium hits highest since May", "summary_original": "China prices up 4%"}]
        self.assertEqual(guardrails.unsupported_numbers("ціна +4% за рік", src), set())
        self.assertEqual(guardrails.unsupported_numbers("доставка скоротиться на 10-14 днів", src), {"10", "14"})

    def test_number_words_in_source_count(self):
        src = [{"title_original": "Aramco cuts Asia prices to six-year low", "summary_original": "over the next four months"}]
        self.assertEqual(guardrails.unsupported_numbers("до 6-річного мінімуму протягом 4 місяців", src), set())
        self.assertEqual(guardrails.unsupported_numbers("на 7 місяців", src), {"7"})

    def test_currency_must_match_source(self):
        src = [{"title_original": "Diesel margins slide", "summary_original": "ICE gasoil crack fell from €85 to €70"}]
        self.assertEqual(guardrails.unsupported_currencies("маржа впала з €85 до €70", src), set())
        self.assertEqual(guardrails.unsupported_currencies("маржа впала з $85 до $70 за барель", src), {"USD"})
        brl = [{"title_original": "Fundo aplica R$ 140 milhões", "summary_original": ""}]
        self.assertEqual(guardrails.unsupported_currencies("140 млн реалів", brl), set())
        self.assertEqual(guardrails.currencies("R$ 140"), {"BRL"})  # «$» у R$ — не долар

    def test_validate_drops_invented_numbers_and_bad_refs(self):
        items = [{"n": 1, "title_original": "Iraq moves 2 million barrels past Hormuz", "summary_original": ""},
                 {"n": 2, "title_original": "Carriers return to Suez in October", "summary_original": ""}]
        raw = {"verdict": "Ризики маршрутів зростають", "why": ["Скорочення на 10-14 днів"],
               "facts": [{"text": "Ірак перевіз 2 млн барелів", "refs": [1]},
                         {"text": "Повернення скоротить шлях на 10-14 днів", "refs": [2]},
                         {"text": "Факт з чужим посиланням", "refs": [99]}],
               "events": [{"text": "Суец", "refs": [2], "type": "Маршрути", "confidence": "mid", "key": True}],
               "related": [{"text": "x", "ref": 77}], "badge": {"text": "Ризик", "tone": "warn"}, "no_news": False}
        brief, problems = _validate(raw, items)
        self.assertEqual([f["text"] for f in brief["facts"]], ["Ірак перевіз 2 млн барелів"])
        self.assertEqual(brief["why"], [])
        self.assertEqual(brief["related"], [])
        self.assertEqual(len(problems), 3)


class DedupTest(unittest.TestCase):
    def test_same_day(self):
        rows = [{"title_original": "Iraq moves crude past Hormuz - Reuters", "summary_original": ""},
                {"title_original": "Iraq moves crude past Hormuz", "summary_original": ""},
                {"title_original": "Poland extends border checks", "summary_original": ""}]
        kept, n = dedup.drop_same_day(rows)
        self.assertEqual(n, 1)
        self.assertEqual(len(kept), 2)

    def test_seen_before(self):
        prev = [{"title_original": "Six vessels hit in Strait of Hormuz since Sunday", "summary_original": ""}]
        rows = [{"title_original": "Six vessels hit in Strait of Hormuz since Sunday", "summary_original": ""},
                {"title_original": "Container lines return to Suez", "summary_original": ""}]
        kept, n = dedup.drop_seen_before(rows, prev)
        self.assertEqual(n, 1)

    def test_canonical_url_strips_tracking(self):
        self.assertEqual(rss.canonicalize_url("HTTPS://Ex.com/a?utm_source=x&id=5#top"), "https://ex.com/a?id=5")


class CompetitorsTest(unittest.TestCase):
    """Фільтри шуму конкурентів."""
    def test_noise(self):
        self.assertTrue(competitors.is_market_noise_title("Tyson Foods stock price today"))
        self.assertTrue(competitors.is_market_noise_title("Vanguard Group LLC buys shares of Tyson Foods"))
        self.assertFalse(competitors.is_market_noise_title("Tyson to close Iowa beef plant"))

    def test_event_category(self):
        self.assertIn("M&A", competitors.classify_event_category("jbs announces acquisition of plant"))

    def test_brief_html_structure(self):
        html = competitor_brief.render_html(
            [{"company": "JBS", "profile": {"Штаб-квартира": "Бразилія"}, "trend": "up", "headline": "Заголовок",
              "bullets": ["пункт"], "events": [{"date": "2026-10-01", "headline": "подія", "category": "фінанси",
                                                "priority": "high", "url": "https://x"}]}], ["теза"], 3, "2026-10-05 01:00")
        for part in ("Зведення по конкурентах за 3 доби", "Головне за період", "▲ Зростання", "1 ключових подій"):
            self.assertIn(part, html)


class PipelineDryRunTest(unittest.TestCase):
    """Увесь конвеєр від новин до digest.json — з імітацією AI."""
    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
            cfg["category_briefs"]["min_news"] = 2
            cfg_path = Path(tmp) / "config.yaml"
            cfg_path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
            code = run.main(["--dry-run", "--config", str(cfg_path), "--input-csv",
                             str(ROOT / "tests/fixtures/raw_news.csv"), "--data-dir", tmp, "--no-competitors"])
            self.assertEqual(code, 0)
            data = json.loads((Path(tmp) / "digest.json").read_text(encoding="utf-8"))
            self.assertGreater(len(data["items"]), 0)
            numbers = {i["n"] for i in data["items"]}
            briefs = [e["brief"] for g in data["market"] for e in g["entries"] if e["brief"]]
            self.assertGreater(len(briefs), 0)
            for b in briefs:  # кожне посилання веде на новину зі стрічки
                for f in b["facts"]:
                    self.assertTrue(set(f["refs"]) <= numbers)
            self.assertTrue(data["today"]["proc"])
            self.assertTrue((Path(tmp) / "daily").glob("news_*.json"))


if __name__ == "__main__":
    unittest.main()
