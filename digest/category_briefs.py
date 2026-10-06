# -*- coding: utf-8 -*-
"""Брифінг по категоріях закупівель і напрямах (вкладка «Ринок закупівель»).
Порядок у довідці — від загального до конкретного: висновок → ключові факти → події й деталі.
Кожен факт і подія посилаються на новини стрічки; числа без джерела не публікуються."""
import hashlib

from . import prompts
from .guardrails import clean_refs, unsupported_currencies, unsupported_numbers
from .llm import LLMError
from .log import log

CONFIDENCE = ["hi", "mid", "lo"]
TONES = ["warn", "ok", "neutral", "none"]

SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string"},
        "why": {"type": "array", "items": {"type": "string"}},
        "facts": {"type": "array", "items": {
            "type": "object",
            "properties": {"text": {"type": "string"}, "refs": {"type": "array", "items": {"type": "integer"}}},
            "required": ["text", "refs"], "additionalProperties": False}},
        "events": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "refs": {"type": "array", "items": {"type": "integer"}},
                "type": {"type": "string"},
                "confidence": {"type": "string", "enum": CONFIDENCE},
                "key": {"type": "boolean"},
            },
            "required": ["text", "refs", "type", "confidence", "key"], "additionalProperties": False}},
        "related": {"type": "array", "items": {
            "type": "object",
            "properties": {"text": {"type": "string"}, "ref": {"type": "integer"}},
            "required": ["text", "ref"], "additionalProperties": False}},
        "badge": {"type": "object",
                  "properties": {"text": {"type": "string"}, "tone": {"type": "string", "enum": TONES}},
                  "required": ["text", "tone"], "additionalProperties": False},
        "no_news": {"type": "boolean"},
    },
    "required": ["verdict", "why", "facts", "events", "related", "badge", "no_news"],
    "additionalProperties": False,
}

PROMPT_FILES = ["category_brief_system", "category_brief"]


def prompt_version() -> str:
    h = hashlib.sha1("".join(prompts.load(n) for n in PROMPT_FILES).encode("utf-8")).hexdigest()
    return h[:8]


def _articles_text(items: list[dict]) -> str:
    lines = []
    for it in items:
        lines.append(
            f"[{it['n']}] {it['date_published_utc'][:10]} · {it.get('source', '')}\n"
            f"    Заголовок: {it.get('title_original', '')}\n"
            f"    Резюме українською: {it.get('ai_summary', '')}\n"
            f"    Опис: {(it.get('summary_original') or '')[:600]}")
    return "\n".join(lines)


def _validate(raw: dict, items: list[dict]) -> tuple[dict, list[str]]:
    """Прибирає неіснуючі посилання і твердження з числами без джерела. Повертає (довідку, проблеми)."""
    by_n = {it["n"]: it for it in items}
    allowed = set(by_n)
    problems = []

    def check(text, refs, where):
        srcs = [by_n[r] for r in refs] if refs else list(by_n.values())
        bad = unsupported_numbers(text, srcs)
        if bad:
            problems.append(f"{where}: числа {sorted(bad)} відсутні в джерелах — «{text[:80]}»")
        bad_cur = unsupported_currencies(text, srcs)
        if bad_cur:
            problems.append(f"{where}: валюта {sorted(bad_cur)} відсутня в джерелах — «{text[:80]}»")
        return not bad and not bad_cur

    out = {"badge": raw.get("badge") or {"text": "", "tone": "neutral"},
           "no_news": bool(raw.get("no_news"))}
    verdict = (raw.get("verdict") or "").strip()
    out["verdict"] = verdict if verdict and check(verdict, None, "висновок") else ""
    out["why"] = [w for w in raw.get("why", []) if w.strip() and check(w, None, "висновок")]
    out["facts"] = []
    for f in raw.get("facts", []):
        refs = clean_refs(f.get("refs"), allowed)
        if not refs:
            problems.append(f"факт без дійсного посилання — «{f.get('text', '')[:80]}»")
        elif check(f.get("text", ""), refs, "факт"):
            out["facts"].append({"text": f["text"], "refs": refs})
    out["events"] = []
    for e in raw.get("events", []):
        refs = clean_refs(e.get("refs"), allowed)
        if refs and check(e.get("text", ""), refs, "подія"):
            out["events"].append({"text": e["text"], "refs": refs, "type": e.get("type", ""),
                                  "confidence": e.get("confidence", "mid"), "key": bool(e.get("key"))})
    out["related"] = [{"text": r["text"], "ref": int(r["ref"])} for r in raw.get("related", [])
                      if clean_refs([r.get("ref")], allowed)]
    return out, problems


def build_one(llm, label: str, kind: str, items: list[dict], period: str) -> dict | None:
    system = prompts.load("category_brief_system")
    prompt = prompts.render("category_brief", kind="Категорія закупівель" if kind == "cat" else "Напрям",
                            name=label, period=period, articles=_articles_text(items))
    brief, problems = None, []
    for attempt in (1, 2):
        try:
            raw = llm.json(system, prompt, max_tokens=4000, schema=SCHEMA, label=label)
        except LLMError as e:
            log(f"[WARN] довідка «{label}»: {e}")
            return None
        brief, problems = _validate(raw, items)
        complete = brief["no_news"] or (brief["verdict"] and brief["facts"])
        if not problems and complete:
            break
        for p in problems:
            log(f"    [перевірка «{label}»] {p}")
        if attempt == 1:  # одна повторна спроба з поясненням, що саме не так
            prompt += ("\n\nПопередня відповідь не пройшла перевірку:\n- " + "\n- ".join(problems or ["немає висновку або фактів"]) +
                       "\nВиправ: використовуй лише числа й валюти, які є в тексті новин, і лише номери новин зі списку.")
    if not brief["no_news"] and not (brief["verdict"] and brief["facts"]):
        log(f"[WARN] довідка «{label}» не пройшла перевірку — показуємо лише перелік новин")
        return None
    return brief


def build_all(llm, cfg: dict, items: list[dict], period: str) -> list[dict]:
    """items — новини закупівель із номером n. Повертає групи для вкладки «Ринок закупівель»."""
    c = cfg["category_briefs"]
    tax = cfg["taxonomy"]
    min_news, max_news = int(c["min_news"]), int(c["max_news_per_brief"])
    profiles = c.get("profiles") or {}
    version = prompt_version()

    def entry(key, label, kind, members):
        members = sorted(members, key=lambda r: (-int(r["ai_score"]), r["date_published_utc"]))
        brief = None
        if c.get("enabled", True) and len(members) >= min_news and kind in ("cat", "dom"):
            log(f"Довідка: {label} — новин: {len(members)}")
            brief = build_one(llm, label, kind, members[:max_news], period)
            if brief is not None:
                brief.update({"profile": [[k, v] for k, v in (profiles.get(label) or {}).items()],
                              "model": llm.model, "prompt_version": version})
        return {"key": key, "label": label, "ids": [m["n"] for m in members], "brief": brief}

    def in_cat(r, cat):
        return cat in [x.strip() for x in (r.get("ai_category") or "").split(",")]

    cats = [entry(f"cat:{c_}", c_, "cat", [r for r in items if in_cat(r, c_)])
            for c_ in tax["categories"] if c_ != "Всі категорії"]
    cats.append(entry("cat:Всі категорії", "Без категорії («Всі категорії»)", "list",
                      [r for r in items if in_cat(r, "Всі категорії")]))
    doms = [entry(f"dom:{k}", v["name"], "dom", [r for r in items if r.get("ai_domain") == k])
            for k, v in tax["domains"].items() if k != "не_релевантно"]
    return [{"group": "Категорії закупівель", "entries": cats}, {"group": "Напрями", "entries": doms}]
