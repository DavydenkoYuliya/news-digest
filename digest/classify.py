# -*- coding: utf-8 -*-
"""AI-класифікація у два етапи:
  1) швидка оцінка лише за заголовками — дешево;
  2) детальний розбір лише новин з оцінкою >= pass1_threshold.
Відповідь — вільним текстом з JSON (без жорсткої схеми): сліпий тест показав, що зі схемою
Haiku пише тексти гірше. Напрям і категорія після відповіді звіряються зі списками config.yaml."""
from difflib import get_close_matches

from . import prompts
from .commodity import commodity_group
from .log import log
from .llm import LLMError


def _fit(value: str, allowed: list[str], fallback: str) -> str:
    """Значення поза списком → найближче зі списку (напр. «энергетика» → «енергетика») або fallback."""
    value = (value or "").strip()
    if value in allowed:
        return value
    close = get_close_matches(value.lower(), allowed, n=1, cutoff=0.75)
    return close[0] if close else fallback


def _clamp(v, lo=1, hi=10):
    try:
        return max(lo, min(hi, int(v)))
    except (TypeError, ValueError):
        return lo


def _batches(rows, size):
    return [rows[i:i + size] for i in range(0, len(rows), size)]


def drop_blocked_prefixes(cfg: dict, rows: list[dict]) -> list[dict]:
    """Рубрики-агрегатори («Morning Bid» тощо) — до прибирання повторів."""
    blocked = [p.lower() for p in cfg["classify"].get("blocked_title_prefixes", [])]
    out = [r for r in rows if not any((r.get("title_original") or "").lower().startswith(p) for p in blocked)]
    if len(rows) - len(out):
        log(f"Агрегатори-рубрики відфільтровано: {len(rows) - len(out)}")
    return out


def drop_irrelevant(cfg: dict, rows: list[dict]) -> list[dict]:
    """Спорт/кіно тощо — після прибирання повторів."""
    junk = [k.lower() for k in cfg["classify"].get("irrelevant_keywords", [])]
    out = [r for r in rows
           if not any(k in ((r.get("title_original") or "") + " " + (r.get("summary_original") or "")).lower()
                      for k in junk)]
    if len(rows) - len(out):
        log(f"Pre-filter (спорт/кіно): {len(rows) - len(out)} статей")
    return out


def run_pass1(llm, cfg, rows) -> list[int]:
    size = int(cfg["classify"]["pass1_batch_size"])
    system = prompts.load("classify_pass1_system")
    scores = []
    batches = _batches(rows, size)
    log(f"[P1] Швидкий скоринг: {len(rows)} статей | {len(batches)} батчів по {size}")
    for b_idx, batch in enumerate(batches, 1):
        lines = [f"{i}. [{(a.get('source') or '')[:40]}] {(a.get('title_original') or '')[:120]}"
                 for i, a in enumerate(batch)]
        prompt = prompts.render("classify_pass1", n=len(batch), articles="\n".join(lines))
        log(f"  [P1] Батч {b_idx}/{len(batches)}")
        try:
            parsed = llm.json(system, prompt, max_tokens=max(len(batch) * 25, 800), label="P1")
            by_id = {int(x["id"]): int(x.get("score", 1)) for x in parsed if isinstance(x, dict) and "id" in x}
        except (LLMError, TypeError, ValueError):
            by_id = {}
        scores.extend(by_id.get(j, 1) for j in range(len(batch)))
    return scores


def run_pass2(llm, cfg, rows) -> list[dict]:
    size = int(cfg["classify"]["pass2_batch_size"])
    tax = cfg["taxonomy"]
    domains, categories = list(tax["domains"].keys()), list(tax["categories"])
    system = prompts.load("classify_pass2_system")
    results, fixed = [], 0
    batches = _batches(rows, size)
    log(f"[P2] Повна класифікація: {len(rows)} статей | {len(batches)} батчів по {size}")
    for b_idx, batch in enumerate(batches, 1):
        lines = [f"{i}. Джерело: {(a.get('source') or '')[:40]}\n"
                 f"   Заголовок: {(a.get('title_original') or '')[:120]}\n"
                 f"   Опис: {(a.get('summary_original') or '')[:500]}"
                 for i, a in enumerate(batch)]
        prompt = prompts.render("classify_pass2", n=len(batch), last_id=len(batch) - 1,
                                articles="\n\n".join(lines),
                                domains="|".join(domains), categories="|".join(categories))
        log(f"  [P2] Батч {b_idx}/{len(batches)}")
        try:
            # 500 токенів на статтю: повний об'єкт ≈350-400 токенів
            parsed = llm.json(system, prompt, max_tokens=min(len(batch) * 500, 8192), label="P2")
            parsed = [x for x in parsed if isinstance(x, dict)]
        except (LLMError, TypeError) as e:
            for _ in batch:
                results.append({"ai_score": 1, "ai_domain": "помилка", "ai_category": "", "ai_country": "",
                                "ai_commodity": "", "ai_summary": "", "ai_detailed": "", "ai_error": str(e)[:80]})
            continue
        by_id = {int(x["id"]): x for x in parsed if "id" in x}
        for j in range(len(batch)):
            x = by_id.get(j, parsed[j] if j < len(parsed) else {})  # без id — за порядком
            domain = _fit(str(x.get("domain", "не_релевантно")), domains, "не_релевантно")
            category = _fit(str(x.get("category", "")), categories, "Всі категорії")
            fixed += (domain != x.get("domain", "не_релевантно")) + (category != x.get("category", ""))
            results.append({
                "ai_score": _clamp(x.get("score", 1)),
                "ai_domain": domain,
                "ai_reason": str(x.get("reason_uk", "")),
                "ai_category": category,
                "ai_country": str(x.get("country", "")),
                "ai_commodity": commodity_group(x.get("commodity", "")),
                "ai_summary": str(x.get("summary_short", "")),
                "ai_detailed": str(x.get("summary_detailed", "")),
            })
    if fixed:
        log(f"[P2] Значень поза довідниками виправлено: {fixed}")
    return results


def classify(llm, cfg: dict, rows: list[dict]) -> list[dict]:
    """Повертає новини з оцінкою >= min_score, відсортовані за оцінкою (спадання)."""
    c = cfg["classify"]
    threshold, min_score = int(c["pass1_threshold"]), int(c["min_score"])
    log(f"До AI: {len(rows)} статей")
    if not rows:
        return []
    scores = run_pass1(llm, cfg, rows)
    relevant = [r for r, s in zip(rows, scores) if s >= threshold]
    log(f"[P1] Результат: {len(relevant)} релевантних (score>={threshold}), {len(rows) - len(relevant)} пропускаємо")
    details = run_pass2(llm, cfg, relevant)
    out = []
    for r, d in zip(relevant, details):
        row = {**r, **d}
        if row["ai_score"] >= min_score:
            out.append(row)
    out.sort(key=lambda r: r["ai_score"], reverse=True)
    log(f"Залишилось (score >= {min_score}): {len(out)} статей")
    if not out:
        # Захист від «тихого» провалу: статті були, а жодна не пройшла — це зламана класифікація.
        raise LLMError("0 статей пройшло фільтр score — AI-класифікація не спрацювала")
    return out
