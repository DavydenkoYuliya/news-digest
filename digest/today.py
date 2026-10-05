# -*- coding: utf-8 -*-
"""«Головне сьогодні»: найважливіші події з довідок по закупівлях + головне з брифінгу конкурентів.
Окремого виклику AI немає — береться з уже готових довідок."""

CONF_RANK = {"hi": 0, "mid": 1, "lo": 2}


def plural_pub(n: int) -> str:
    a, b = n % 10, n % 100
    word = "публікація" if a == 1 and b != 11 else "публікації" if 2 <= a <= 4 and not 12 <= b <= 14 else "публікацій"
    return f"{n} {word}"


def build(market_groups: list[dict], items_by_n: dict, competitor_highlights: list[str], limit: int) -> dict:
    candidates = []
    for group in market_groups:
        for entry in group["entries"]:
            brief = entry.get("brief")
            if not brief:
                continue
            for ev in brief.get("events", []):
                if not ev.get("key"):
                    continue
                refs = ev["refs"]
                top_score = max(int(items_by_n[r]["ai_score"]) for r in refs)
                candidates.append(((CONF_RANK.get(ev["confidence"], 2), -len(refs), -top_score),
                                   {"t": ev["text"], "m": f"{plural_pub(len(refs))} · {entry['label']}",
                                    "conf": ev["confidence"], "go": entry["key"], "refs": refs}))
    candidates.sort(key=lambda c: c[0])
    chosen, used = [], set()
    for _, item in candidates:
        if used & set(item["refs"]):  # та сама подія з іншої категорії/напряму
            continue
        chosen.append(item)
        used |= set(item["refs"])
        if len(chosen) >= limit:
            break
    return {"proc": chosen, "comp": competitor_highlights}
