# -*- coding: utf-8 -*-
"""Читання RSS — спільне для загальних новин і конкурентів."""
import datetime as dt
import re
import socket
import ssl
import time
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as dateparser, tz

from .log import log

feedparser.USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
socket.setdefaulttimeout(30)

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_name", "utm_reader", "utm_social", "utm_viz_id",
    "gclid", "fbclid", "mc_cid", "mc_eid", "mkt_tok", "igshid",
}


def configure_ssl(verify: bool):
    """verify=False — лише для корпоративних проксі, що підміняють сертифікати."""
    if not verify and hasattr(ssl, "_create_unverified_context"):
        ssl._create_default_https_context = ssl._create_unverified_context


def now_utc():
    return dt.datetime.now(tz=tz.UTC)


def strip_html(text: str) -> str:
    if not text:
        return ""
    return " ".join(BeautifulSoup(text, "html.parser").get_text(" ").split())


def canonicalize_url(url: str) -> str:
    if not url:
        return url
    try:
        p = urlparse(url)
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in TRACKING_PARAMS]
        return urlunparse((p.scheme.lower() if p.scheme else "http", p.netloc.lower(), p.path, p.params,
                           urlencode(q, doseq=True), ""))
    except Exception:
        return url


def parse_entry_datetime(entry):
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if t:
        try:
            return dt.datetime(*t[:6], tzinfo=tz.UTC)
        except Exception:
            pass
    for k in ("published", "updated", "pubDate"):
        if entry.get(k):
            try:
                d = dateparser.parse(entry[k])
                if not d.tzinfo:
                    d = d.replace(tzinfo=tz.UTC)
                return d.astimezone(tz.UTC)
            except Exception:
                pass
    return None


def read_feed_list(path) -> list[str]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def fetch(feed: str):
    """Повертає (назва_джерела, список записів). Записи — словники з уже очищеними полями."""
    log(f"Reading feed: {feed}")
    is_google = "news.google.com" in feed
    if is_google:
        time.sleep(1)  # не перевантажувати Google News
    try:
        parsed = feedparser.parse(feed)
    except Exception as e:
        log(f"[ERROR] Failed to parse feed: {feed} - {e}")
        return urlparse(feed).netloc, []

    source = parsed.feed.get("title", urlparse(feed).netloc) if hasattr(parsed, "feed") else urlparse(feed).netloc
    if not parsed.entries:
        if hasattr(parsed, "status"):
            log(f"[WARN] 0 entries from feed (HTTP {parsed.status}): {feed}")
        else:
            log(f"[WARN] 0 entries from feed: {feed}")
        return source, []

    out = []
    for e in parsed.entries:
        link = e.get("link")
        title = strip_html(e.get("title", ""))
        if is_google:  # Google News дописує « - Видання» в кінець заголовка
            title = re.sub(r'\s[-–]\s[^-–]{2,60}$', '', title).strip()
        summary_plain = strip_html(e.get("summary", ""))
        content_list = e.get("content", [])
        if content_list:
            full = strip_html(content_list[0].get("value", ""))
            summary = full if len(full) > len(summary_plain) else summary_plain
        else:
            summary = summary_plain
        if is_google:  # справжній видавець замість «Google News»
            src = e.get("source", {})
            if isinstance(src, dict) and src.get("title"):
                display_source = src["title"]
            elif link:
                display_source = urlparse(link).netloc.replace("www.", "")
            else:
                display_source = source
        else:
            display_source = source
        out.append({
            "link": link, "title": title, "summary": summary,
            "pub": parse_entry_datetime(e),
            "tags": [t.get("term", "").lower() for t in e.get("tags", [])],
            "source": display_source, "feed_source": source, "feed": feed,
            "entry_id": e.get("id", e.get("guid", "")),
        })
    return source, out
