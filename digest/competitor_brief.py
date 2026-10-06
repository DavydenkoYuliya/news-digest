# -*- coding: utf-8 -*-
"""Брифінг по конкурентах — БЕЗ ЗМІН відносно competitor_brief.py: ті самі профілі, інструкції для AI
і HTML. Відмінність лише технічна: читає новини конкурентів напряму (без проміжних CSV)
і звертається до AI через llm.py. Назви компаній і профілі — у competitors.yaml."""
import datetime as dt

from . import prompts
from .competitors import COMPETITORS, published
from .llm import LLMError
from .log import log

TREND = {
    "up":    ("▲", "Зростання", "#1a7f37", "#e6f4ea"),
    "down":  ("▼", "Під тиском", "#c0392b", "#fdecea"),
    "mixed": ("◆", "Суперечливо", "#b26a00", "#fdf3e2"),
    "flat":  ("●", "Без змін", "#666", "#eef0f2"),
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _cap(s):
    s = str(s).strip()
    return s[:1].upper() + s[1:] if s else s


def render_html(blocks, highlights, days, date_str):
    css = """
    body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;padding:24px;
      background:linear-gradient(135deg,#06111f 0%,#0d2137 40%,#1a3a5c 100%);
      background-attachment:fixed;color:#1a1a1a;line-height:1.45}
    .wrap{max-width:1000px;margin:0 auto}
    h1{font-size:22px;margin:0 0 4px;color:#fff}
    .sub{color:rgba(255,255,255,.65);margin:0 0 20px;font-size:13px}
    .card{background:#fff;border:1px solid #e3e5e8;border-radius:10px;padding:18px 20px;margin:0 0 16px;
      box-shadow:0 1px 2px rgba(0,0,0,.04)}
    .exec{background:#fff;border:1px solid #d7deea;border-left:4px solid #2557a7;border-radius:10px;
      padding:16px 20px;margin:0 0 22px}
    .exec h2{font-size:14px;margin:0 0 10px;color:#2557a7;text-transform:uppercase;letter-spacing:.04em}
    .exec ol{margin:0;padding-left:20px}.exec li{margin:0 0 6px;font-size:14px;color:#222}
    .co{font-size:17px;font-weight:700;margin:0 0 6px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
    .badge{border-radius:20px;font-size:11px;padding:2px 10px;font-weight:700}
    .co .n{background:#eef1f6;color:#556;border-radius:20px;font-size:11px;padding:2px 9px;font-weight:600}
    .profile{margin:0 0 12px;padding:9px 12px;background:#f7f8fa;border-radius:6px;
      border-left:3px solid #c9ccd1;display:grid;grid-template-columns:auto 1fr;
      column-gap:10px;row-gap:3px;font-size:12.5px}
    .profile .pl{color:#8b93a1;font-weight:600;white-space:nowrap}
    .profile .pv{color:#3a3f47}
    .verdict{font-size:15px;font-weight:700;color:#1a1a1a;margin:0 0 8px;line-height:1.35}
    .bullets{margin:0 0 12px;padding-left:18px;list-style:disc}
    .bullets li{color:#3a3f47;font-size:13.5px;margin:0 0 4px;line-height:1.4}
    table{width:100%;border-collapse:collapse;font-size:13px}
    th,td{text-align:left;padding:7px 9px;border-bottom:1px solid #eee;vertical-align:top}
    th{background:#fafbfc;color:#555;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.03em}
    td.date{white-space:nowrap;color:#666}
    tr.hi td{background:#fffdf5}
    .dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px;vertical-align:middle}
    .cat{display:inline-block;background:#f0f3f8;border-radius:5px;padding:1px 7px;font-size:11px;color:#456}
    td a{color:#1a3a5c;text-decoration:none}
    td a:hover{color:#2557a7;text-decoration:underline}
    .none{color:#999;font-style:italic;font-size:13px}
    @media print{body{background:#fff}.card,.exec{box-shadow:none;break-inside:avoid}}
    """
    html = ["<!doctype html><html lang='uk'><head><meta charset='utf-8'>",
            "<meta name='viewport' content='width=device-width,initial-scale=1'>",
            f"<title>Брифінг по конкурентах — {date_str}</title><style>{css}</style></head><body><div class='wrap'>",
            f"<h1>Зведення по конкурентах за {days} доби</h1>",
            f"<p class='sub'>Згенеровано {date_str} · AI-підсумок на основі новинного треку · світові лідери м'яса птиці</p>"]

    # Топ-зведення (крос-компанійне)
    if highlights:
        html.append("<div class='exec'><h2>🔎 Головне за період</h2><ol>")
        for h in highlights:
            html.append(f"<li>{esc(h)}</li>")
        html.append("</ol></div>")

    for b in blocks:
        html.append("<div class='card'>")
        tr = TREND.get(b.get("trend", "flat"), TREND["flat"])
        evs = b.get("events") or []
        key_n = len(evs)
        badge = (f"<span class='badge' style='color:{tr[2]};background:{tr[3]}'>{tr[0]} {tr[1]}</span>"
                 if evs else "")
        cnt = f"<span class='n'>{key_n} ключових подій</span>" if evs else ""
        html.append(f"<div class='co'>{esc(b['company'])} {badge} {cnt}</div>")
        if b.get("profile"):
            html.append("<div class='profile'>")
            for label, value in b["profile"].items():
                html.append(f"<div class='pl'>{esc(label)}</div><div class='pv'>{esc(value)}</div>")
            html.append("</div>")
        if evs and b.get("headline"):
            html.append(f"<div class='verdict'>{esc(b['headline'])}</div>")
        bullets = b.get("bullets") or []
        if bullets:
            html.append("<ul class='bullets'>")
            for bl in bullets:
                html.append(f"<li>{esc(bl)}</li>")
            html.append("</ul>")
        if b.get("no_news") or not evs:
            html.append("<div class='none'>Без суттєвих подій за період.</div>")
        else:
            evs = sorted(evs, key=lambda e: 0 if e.get("priority") == "high" else 1)
            html.append("<table><thead><tr><th>Дата</th><th>Подія</th><th>Категорія</th></tr></thead><tbody>")
            for e in evs:
                hi = "hi" if e.get("priority") == "high" else ""
                dot = "#c0392b" if e.get("priority") == "high" else "#c9ccd1"
                headline_esc = esc(e.get("headline", ""))
                url = e.get("url", "")
                headline_html = (
                    f"<a href='{esc(url)}' target='_blank' rel='noopener noreferrer'>{headline_esc}</a>"
                    if url else headline_esc
                )
                html.append(
                    f"<tr class='{hi}'><td class='date'>{esc(e.get('date',''))}</td>"
                    f"<td><span class='dot' style='background:{dot}'></span>{headline_html}</td>"
                    f"<td><span class='cat'>{esc(_cap(e.get('category','')))}</span></td></tr>")
            html.append("</tbody></table>")
        html.append("</div>")
    html.append("</div></body></html>")
    return "\n".join(html)


def load_events(rows: list[dict], days: int) -> list[dict]:
    """Рядки за останні N діб (за date_published_utc), новіші згори."""
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    out = []
    for r in rows:
        d = r.get("date_published_utc", "")
        try:
            pub = dt.datetime.strptime(d[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc)
        except Exception:
            pub = None
        if pub and pub < cutoff:
            continue
        out.append({
            "date": d[:10],
            "brand": r.get("ai_category", "") or r.get("entity", ""),
            "category": r.get("event_category", ""),
            "title": r.get("title_uk", "") or r.get("title_original", ""),
            "source": r.get("source", ""),
            "url": r.get("url", ""),
        })
    out.sort(key=lambda x: x["date"], reverse=True)
    return out


def summarize(llm, company, events, days):
    sliced = events[:40]
    lines = [f'{i}. [{e["date"]}] ({e["brand"]}; {e["category"]}) {e["title"]} — {e["source"]}'
             for i, e in enumerate(sliced)]
    prompt = prompts.render("competitor_brief", company=company, days=days,
                            joined="\n".join(lines) if lines else "(новин за період немає)")
    try:
        result = llm.json(prompts.load("competitor_brief_system"), prompt, max_tokens=2000, label=company)
        # Реальний URL підставляємо за індексом джерела (AI не відтворює довгі посилання сам)
        for ev in result.get("events", []):
            idx = ev.get("source_idx")
            if isinstance(idx, int) and 0 <= idx < len(sliced):
                ev["url"] = sliced[idx].get("url", "")
        return result
    except LLMError as ex:
        log(f"[WARN] {company}: {ex}")
        return {"summary": "(не вдалося згенерувати підсумок)", "events": [], "no_news": True}


def make_highlights(llm, blocks, days):
    """Крос-компанійне «Головне за N діб» — 3-5 ранжованих тез по всіх конкурентах."""
    parts = [f"{b['company']}: {b.get('headline') or '; '.join(b.get('bullets') or [])}"
             for b in blocks if b.get("events")]
    if not parts:
        return []
    try:
        data = llm.json(prompts.load("competitor_highlights_system"),
                        prompts.render("competitor_highlights", days=days, parts="\n".join(parts)),
                        max_tokens=700, label="highlights")
        return data.get("highlights", [])
    except LLMError as ex:
        log(f"[WARN] highlights: {ex}")
        return []


def build(llm, rows_by_producer: dict, days: int):
    """Повертає (html, highlights)."""
    blocks = []
    for key in published():
        name = COMPETITORS[key]["name"]
        events = load_events(rows_by_producer.get(key, []), days)
        log(f"{name}: {len(events)} новин за {days} діб")
        res = summarize(llm, name, events, days) if events else {"bullets": [], "events": [], "no_news": True}
        blocks.append({"company": name, "count": len(events),
                       "profile": COMPETITORS[key].get("profile", ""),
                       "trend": res.get("trend", "flat"), "headline": res.get("headline", ""),
                       "bullets": res.get("bullets", []), "events": res.get("events", []),
                       "no_news": res.get("no_news", False)})
    highlights = make_highlights(llm, blocks, days)
    html = render_html(blocks, highlights, days, dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    return html, highlights
