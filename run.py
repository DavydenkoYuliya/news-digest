# -*- coding: utf-8 -*-
"""AI Дайджест новин — нічний запуск, одна команда:

    python run.py               звичайний запуск (збір → AI → конкуренти → довідки → файли для сайту)
    python run.py --dry-run     перевірка без ключа і без витрат (AI імітується)

Налаштування: config.yaml (методика, ліміти), .env (провайдер AI і ключ), prompts/ (інструкції для AI)."""
import argparse
import csv
import datetime as dt
import sys
import time
from pathlib import Path

from digest import category_briefs, classify, collect, competitor_brief, competitors, dedup, rss, today
from digest.config import load, path
from digest.log import log
from digest.llm import LLM, LLMError
from digest.store import Store

SCHEMA_VERSION = 2  # версія формату digest.json (1 — перша версія, без цього поля)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="AI Дайджест новин — нічний запуск")
    ap.add_argument("--dry-run", action="store_true", help="без AI: перевірка, що конвеєр працює")
    ap.add_argument("--config", help="інший файл налаштувань замість config.yaml")
    ap.add_argument("--days", type=int, help="за скільки діб збирати новини (за замовчуванням — з останнього запуску)")
    ap.add_argument("--input-csv", help="взяти вже зібрані новини з CSV (колонки як у щоденних файлах: date_published_utc, source, title_original, summary_original, url) замість RSS")
    ap.add_argument("--data-dir", help="куди писати результат (за замовчуванням — папка даних сайту)")
    ap.add_argument("--no-competitors", action="store_true", help="пропустити трек і брифінг конкурентів")
    ap.add_argument("--no-briefs", action="store_true", help="пропустити довідки по категоріях")
    ap.add_argument("--no-prev-dedup", action="store_true", help="не прибирати повтори з попередніми днями")
    return ap.parse_args(argv)


def collection_days(store: Store, cfg: dict, today_: dt.date, forced: int | None) -> int:
    """Збираємо лише нові дні з моменту останнього запуску (1..7)."""
    if forced:
        return forced
    last = store.latest_day()
    if not last:
        return int(cfg["collect"]["days"])
    return max(1, min(7, (today_ - last).days))


def read_csv(p: str) -> list[dict]:
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def site_item(row: dict, n: int) -> dict:
    date = row.get("date_published_utc", "")
    competitor = bool(row.get("producer"))
    return {
        "n": n,
        "section": "competitor" if competitor else "news",
        "date": date.replace(" ", "T") + "Z" if date else "",
        "source": row.get("source", ""),
        # заголовок на сайті = AI-резюме (або переклад/оригінал)
        "title": row.get("ai_summary") or row.get("title_uk") or row.get("title_original", ""),
        "summary": row.get("ai_summary", ""),
        "detailed": row.get("ai_detailed", ""),
        "domain": row.get("ai_domain", ""),
        "category": row.get("ai_category", ""),
        "country": row.get("ai_country", ""),
        "commodity": row.get("ai_commodity", ""),
        "url": row.get("url", ""),
        "score": int(row.get("ai_score") or 0),
        "company": row.get("ai_domain", "") if competitor else "",
    }


def period_label(rows: list[dict]) -> str:
    dates = sorted(r["date_published_utc"][:10] for r in rows if r.get("date_published_utc"))
    if not dates:
        return ""
    a, b = dt.date.fromisoformat(dates[0]), dt.date.fromisoformat(dates[-1])
    return f"{a:%d.%m}–{b:%d.%m.%Y}"


def main(argv=None) -> int:
    args = parse_args(argv)
    started = time.time()
    cfg = load(Path(args.config) if args.config else None)
    rss.configure_ssl(cfg["collect"].get("verify_ssl", True))
    store = Store(cfg, Path(args.data_dir) if args.data_dir else None)
    today_ = dt.datetime.now(dt.timezone.utc).date()

    try:
        if args.dry_run:
            from digest.fake_llm import FakeLLM
            llm = FakeLLM(cfg)
        else:
            llm = LLM(cfg)
    except LLMError as e:
        log(f"[FATAL] {e}")
        return 2
    log(f"AI: {llm.provider} / {llm.model}")

    # 1. Збір загальних новин
    if args.input_csv:
        raw = read_csv(args.input_csv)
        log(f"Новини з файлу {args.input_csv}: {len(raw)}")
    else:
        days = collection_days(store, cfg, today_, args.days)
        raw = collect.collect_news(cfg, days)

    # 2. Прибирання повторів і шуму
    rows = classify.drop_blocked_prefixes(cfg, raw)
    if not args.no_prev_dedup:
        d = cfg["dedup"]
        prev = store.previous_rows(today_, int(d["previous_days_to_check"]), int(d["lookback_calendar_days"]))
        rows, n = dedup.drop_seen_before(rows, prev)
        if n:
            log(f"Дублікати з попередніх днів: {n}")
    rows, n = dedup.drop_same_day(rows)
    if n:
        log(f"Внутрішньоденні дублікати: {n}")
    rows = classify.drop_irrelevant(cfg, rows)

    # 3. AI-класифікація
    try:
        classified = classify.classify(llm, cfg, rows)
    except LLMError as e:
        log(f"[FATAL] {e}")
        return 1
    store.save_daily(today_, classified)
    log(f"AI на класифікацію: {llm.usage}")

    # 4. Зведення за 3 останні дні + конкуренти, одна подія — один рядок
    combined = [r for _, day_rows in store.last_days(3) for r in day_rows]
    comp_rows = {}
    if cfg["competitors"].get("enabled", True) and not args.no_competitors:
        comp_rows = competitors.collect_all(llm, cfg)
        combined += [r for key in competitors.published() for r in comp_rows.get(key, [])]
    combined.sort(key=lambda r: -int(r.get("ai_score") or 0))
    combined, n = dedup.drop_similar_summaries(combined)
    log(f"Дедуплікація за AI-резюме: видалено {n}, залишилось {len(combined)}")
    for i, r in enumerate(combined, 1):
        r["n"] = i

    # 5. Брифінг конкурентів
    highlights = []
    if comp_rows:
        html, highlights = competitor_brief.build(llm, comp_rows, int(cfg["competitors"]["days"]))
        brief_path = store.dir / "competitor_brief.html" if args.data_dir else path(cfg, cfg["publish"]["competitor_brief_file"])
        brief_path.write_text(html, encoding="utf-8")
        log(f"Брифінг конкурентів: {brief_path}")

    # 6. Брифінг по категоріях і «Головне сьогодні»
    news_items = [r for r in combined if not r.get("producer")]
    period = period_label(news_items)
    market = []
    if not args.no_briefs:
        market = category_briefs.build_all(llm, cfg, news_items, period)
    today_block = today.build(market, {r["n"]: r for r in news_items}, highlights,
                              int(cfg["today"]["procurement_items"]))

    # 7. Файл для сайту
    # Формат файлу описаний у README («Файл даних сайту»); при несумісних змінах — збільшити SCHEMA_VERSION.
    store.write_digest({
        "schema_version": SCHEMA_VERSION,
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "period": period,
        "model": llm.model,
        "prompt_version": category_briefs.prompt_version(),
        "domains": cfg["taxonomy"]["domains"],
        "min_news": int(cfg["category_briefs"]["min_news"]),
        "items": [site_item(r, r["n"]) for r in combined],
        "market": market,
        "today": today_block,
    })
    store.prune(int(cfg["dedup"]["keep_full_days"]), today_)
    log(f"Готово за {time.time() - started:.0f} с · {len(combined)} новин · AI: {llm.usage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
