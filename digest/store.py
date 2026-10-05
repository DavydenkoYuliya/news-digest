# -*- coding: utf-8 -*-
"""Файли даних. Усе лежить в одній папці сайту (config.yaml → publish.site_data_dir):
  daily/news_<дата>.json — класифіковані новини дня (для прибирання повторів і зведення за 3 дні);
                           зберігаються keep_full_days днів, старші видаляються автоматично;
  digest.json            — те, що показує сайт (стрічка, довідки, «Головне сьогодні»)."""
import datetime as dt
import json
from pathlib import Path

from .config import path
from .log import log


class Store:
    def __init__(self, cfg: dict, data_dir: Path | None = None):
        self.dir = data_dir or path(cfg, cfg["publish"]["site_data_dir"])
        self.daily = self.dir / "daily"
        self.daily.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ щоденні файли
    def daily_file(self, day: dt.date) -> Path:
        return self.daily / f"news_{day.isoformat()}.json"

    def save_daily(self, day: dt.date, rows: list[dict]):
        self.daily_file(day).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")

    def load_daily(self, p: Path) -> list[dict]:
        return json.loads(p.read_text(encoding="utf-8"))

    def daily_files(self) -> list[Path]:
        return sorted(self.daily.glob("news_*.json"))

    @staticmethod
    def day_of(p: Path) -> dt.date:
        return dt.date.fromisoformat(p.stem.replace("news_", ""))

    def latest_day(self) -> dt.date | None:
        files = self.daily_files()
        return self.day_of(files[-1]) if files else None

    def previous_rows(self, today: dt.date, wanted: int, lookback: int) -> list[dict]:
        """Новини з `wanted` наявних попередніх днів у межах `lookback` календарних днів."""
        rows, found = [], 0
        for delta in range(1, lookback + 1):
            if found >= wanted:
                break
            p = self.daily_file(today - dt.timedelta(days=delta))
            if p.exists():
                rows.extend(self.load_daily(p))
                found += 1
        if not found:
            log(f"[!] Немає щоденних файлів за {lookback} дн. — повтори з попередніми днями не прибираються")
        return rows

    def last_days(self, n: int) -> list[tuple[dt.date, list[dict]]]:
        return [(self.day_of(p), self.load_daily(p)) for p in self.daily_files()[-n:]]

    def prune(self, keep_days: int, today: dt.date):
        limit = today - dt.timedelta(days=keep_days)
        for p in self.daily_files():
            if self.day_of(p) < limit:
                p.unlink()
                log(f"Видалено старий щоденний файл: {p.name}")

    # ------------------------------------------------------------------ сайт
    def write_digest(self, payload: dict):
        tmp = self.dir / "digest.json.tmp"
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.dir / "digest.json")  # атомарно: сайт ніколи не побачить напівзаписаний файл
