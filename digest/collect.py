# -*- coding: utf-8 -*-
"""Збір загальних новин з RSS."""
import datetime as dt
from collections import defaultdict

try:
    from langdetect import detect
except Exception:  # бібліотека не обов'язкова
    def detect(_):
        return "unknown"

from . import rss
from .config import path
from .log import log


def collect_news(cfg: dict, days: int) -> list[dict]:
    c = cfg["collect"]
    exclude = {x.lower() for x in c.get("exclude_rss_categories", [])}
    max_per_source = int(c.get("max_per_source", 0))
    feeds = rss.read_feed_list(path(cfg, c["feeds_file"]))

    now = rss.now_utc()
    cutoff = now - dt.timedelta(days=days)
    seen, out = set(), []
    per_source = defaultdict(int)

    for feed in feeds:
        source, entries = rss.fetch(feed)
        for e in entries:
            if exclude and any(t in exclude for t in e["tags"]):
                continue
            if max_per_source and per_source[source] >= max_per_source:
                continue
            if not e["link"]:
                continue
            pub = e["pub"] or now          # без дати — вважаємо свіжою, щоб не губити новину
            if pub < cutoff or pub > now:  # дата в майбутньому — помилка джерела
                continue
            key = rss.canonicalize_url(e["link"])
            if key in seen:
                continue
            seen.add(key)
            text = f"{e['title']} {e['summary']}".strip()
            out.append({
                "date_published_utc": pub.strftime("%Y-%m-%d %H:%M:%S"),
                "source": e["source"],
                "feed_url": feed,
                "lang_detected": detect(text) if text else "unknown",
                "title_original": e["title"],
                "summary_original": e["summary"],
                "url": e["link"],
                "url_canonical": key,
                "categories": ";".join(e["tags"]),
                "entry_id": e["entry_id"],
            })
            per_source[source] += 1

    out.sort(key=lambda r: r["date_published_utc"], reverse=True)
    log(f"Зібрано новин: {len(out)} з {len(feeds)} джерел (за {days} дн.)")
    return out
