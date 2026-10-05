# -*- coding: utf-8 -*-
"""Прибирання повторів. Пороги і правила перенесено з ai_classify_v2.py та combine_digest.py без змін."""
import re
from difflib import SequenceMatcher


def _norm(title: str) -> str:
    return re.sub(r"\s*[-–|]\s*\w[\w\s]{0,30}$", "", title).lower().strip()


def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def drop_seen_before(rows: list[dict], previous_rows: list[dict]) -> tuple[list[dict], int]:
    """Новини, що вже були в дайджестах попередніх днів (заголовок ≥0.72 або опис ≥0.70)."""
    prev = []
    for r in previous_rows:
        t = (r.get("title_original") or "").lower().strip()
        s = (r.get("summary_original") or "")[:150].lower().strip()
        if t:
            prev.append((_norm(t), s))

    def is_dup(r):
        nt = _norm(r.get("title_original", ""))
        ns = (r.get("summary_original") or "")[:150].lower().strip()
        for pt, ps in prev:
            if _sim(nt, pt) >= 0.72:
                return True
            if ns and ps and _sim(ns, ps) >= 0.70:
                return True
        return False

    kept = [r for r in rows if not is_dup(r)]
    return kept, len(rows) - len(kept)


def drop_same_day(rows: list[dict]) -> tuple[list[dict], int]:
    """Повтори в межах одного збору (заголовок ≥0.55 або опис ≥0.65)."""
    seen, kept = [], []
    for r in rows:
        nt = _norm(r.get("title_original", ""))
        ns = (r.get("summary_original") or "")[:150].lower().strip()
        if any(_sim(nt, st) >= 0.55 or (ns and ss and _sim(ns, ss) >= 0.65) for st, ss in seen):
            continue
        seen.append((nt, ns))
        kept.append(r)
    return kept, len(rows) - len(kept)


def drop_similar_summaries(rows: list[dict]) -> tuple[list[dict], int]:
    """Фінальне склеювання дайджесту за AI-резюме (як combine_digest.py): одна подія з кількох джерел.
    rows мають бути відсортовані за оцінкою (спадання) — лишається стаття з вищою оцінкою."""
    def sim(a, b, threshold):
        m = SequenceMatcher(None, a.lower().strip(), b.lower().strip())
        if m.real_quick_ratio() < threshold:
            return 0.0
        return m.ratio()

    seen_summaries, seen_by_ctx, kept = [], {}, []
    for r in rows:
        summary = (r.get("ai_summary") or "").strip()
        title = (r.get("title_original") or "").strip()
        ctx = ((r.get("ai_domain") or "").strip(), (r.get("ai_country") or "").strip())
        dup = False
        if summary and any(s and sim(summary, s, 0.70) >= 0.70 for s in seen_summaries):
            dup = True
        if not dup and ctx[0]:
            for s_sum, s_title in seen_by_ctx.get(ctx, []):
                if (summary and s_sum and sim(summary, s_sum, 0.45) >= 0.45) or \
                   (title and s_title and sim(title, s_title, 0.55) >= 0.55):
                    dup = True
                    break
        if dup:
            continue
        seen_summaries.append(summary)
        seen_by_ctx.setdefault(ctx, []).append((summary, title))
        kept.append(r)
    return kept, len(rows) - len(kept)
