# -*- coding: utf-8 -*-
"""Трек новин по конкурентах — як competitor_digest.py, без змін логіки відбору.
Сутності, категорії подій і фільтри шуму — regex (без AI). Єдина відмінність: переклад
заголовків і описів робить той самий AI (замість неофіційної бібліотеки translators)."""
import datetime as dt
import re

try:
    from langdetect import detect
except Exception:
    def detect(_):
        return "unknown"

from . import prompts, rss
from .competitors_config import COMPETITORS, EVENT_CATEGORIES, RELEVANCE_SCORE_MAP
from .config import path
from .llm import LLMError
from .log import log

DOMAIN_LABELS = {
    "pilgrims": "Pilgrim's",
    "tyson": "Tyson",
    "brf": "BRF",
    "ldc_groupe": "LDC",
    "louis_dreyfus": "Louis Dreyfus",
    "jbs": "JBS",
}


def match_entities(text_l: str, entities: list) -> list:
    """Повертає список (entity_dict, matched_in_title_bool) для всіх сутностей, що збіглись."""
    matched = []
    for ent in entities:
        hit = any(re.search(p, text_l) for p in ent["keywords"])
        if not hit:
            continue
        # Скоуп-обмеження: JBS рахуємо лише за наявності прямого контексту PPC
        req_ctx = ent.get("requires_context")
        if req_ctx and not any(re.search(p, text_l) for p in req_ctx):
            continue
        # Мінус-слова: відкидаємо омонімічні хиби (Perdigão-місто/прізвище,
        # "sadia"-прикметник тощо) — якщо є будь-яке стоп-слово, це не наша сутність.
        excl = ent.get("exclude")
        if excl and any(re.search(p, text_l) for p in excl):
            continue
        matched.append(ent)
    return matched


# Стоп-слова (pt/en) для кластеризації подій — службові слова, що не несуть теми.
_CLUSTER_STOP = set(
    "de da do dos das com para que uma como veja apos após pela pelo nos nas por "
    "sobre entre seus suas mais ainda hoje the and for with from this that after "
    "into news inc company global foods".split()
)


def _money_sig(t: str) -> set:
    """Грошові суми (R$ X / X milhões|bilhões) — найсильніша сигнатура тієї самої
    події: два заголовки з тією ж сумою — майже напевно про одну новину."""
    s = set()
    for m in re.finditer(r"r\$\s*([\d.,]+)|([\d.,]+)\s*(?:milh|mi\b|bilh|bi\b)", t.lower()):
        v = re.sub(r"\D", "", (m.group(1) or m.group(2) or ""))
        if v:
            s.add(v)
    return s


def _event_tokens(t: str, entity_stop: set) -> set:
    words = re.sub(r"[^0-9a-zà-ÿ\s]", " ", t.lower()).split()
    return set(
        w for w in words
        if len(w) >= 4 and w not in _CLUSTER_STOP and w not in entity_stop
    )


def fuzzy_dedup(rows: list, jaccard: float = 0.42) -> list:
    """Схлопує майже-дублі В МЕЖАХ однієї сутності (мультисутність зберігаємо):
      • спільна грошова сума (R$ 47 mi / R$ 579 mi) → та сама подія;
      • інакше — перетин інформативних токенів (Jaccard ≥ поріг);
      • різні грошові суми (47 vs 134) майже ніколи не зливаємо (поріг 0.8).
    Назви сутності вилучаються з токенів, щоб різні події про ту саму компанію
    не злипались. Без зовнішніх залежностей; різномовні переклади тієї самої події
    НЕ ловить (для цього потрібні embeddings — свідомо поза скоупом news-only треку)."""
    kept = []
    reps = {}  # entity -> list[(tokens, money)]
    for r in rows:
        ent = r["entity"]
        ent_stop = set(w for w in re.split(r"\W+", ent.lower()) if len(w) >= 4)
        tk = _event_tokens(r["title_original"], ent_stop)
        mn = _money_sig(r["title_original"])
        lst = reps.setdefault(ent, [])
        is_dup = False
        for (tk2, mn2) in lst:
            if mn and mn2 and (mn & mn2):
                is_dup = True
                break
            if not tk or not tk2:
                continue
            j = len(tk & tk2) / len(tk | tk2)
            thr = 0.8 if (mn and mn2 and not (mn & mn2)) else jaccard
            if j >= thr:
                is_dup = True
                break
        if not is_dup:
            lst.append((tk, mn))
            kept.append(r)
    return kept


def classify_event_category(text_l: str) -> str:
    hits = []
    for category, patterns in EVENT_CATEGORIES.items():
        if any(re.search(p, text_l) for p in patterns):
            hits.append(category)
    return "; ".join(hits) if hits else "інше"


STALE_QUARTER_RE = re.compile(
    r'\bQ([1-4])\s+(\d{4})\b|\b([1-4])(?:st|nd|rd|th)?\s+quarter\s+(?:of\s+)?(\d{4})\b',
    re.IGNORECASE,
)


def is_stale_earnings_title(title: str, now_dt) -> bool:
    """TipRanks та подібні сайти повторно індексуються Google News зі старими
    архівними сторінками звітів (напр. "Q2 2025 Earnings Report") зі СВІЖОЮ
    датою pubDate — тому фільтр за датою їх не ловить. Ловимо за роком/кварталом
    у заголовку: рахуємо вік у кварталах і відкидаємо матеріали, що на ≥2 квартали
    старіші за поточний (лишається лише актуальний квартал)."""
    m = STALE_QUARTER_RE.search(title)
    if not m:
        return False
    q = int(m.group(1) or m.group(3))
    year = int(m.group(2) or m.group(4))
    cur_q = (now_dt.month - 1) // 3 + 1
    title_idx = year * 4 + (q - 1)
    cur_idx = now_dt.year * 4 + (cur_q - 1)
    return (cur_idx - title_idx) >= 2


# ---- Стоп-фільтр «не-новинних» сторінок і біржового шуму власників акцій ----
# Статичні сторінки котирувань / форуми / ADR-BDR-лістинги / 13F.
STOP_PAGE_RE = re.compile(
    r'\bstock price\b|\bstock quote\b|\bstock forecast\b|\bprice history\b|'
    r'\bstock (?:discussion|forum|statistics|latest news)\b|\bdiscussion & forum\b|'
    r'\bmessage board\b|\bvaluation metrics\b|\bfinancials?:\s|\bpeers comparison\b|'
    r'\bvs\.? peers\b|\binsider activity\b|\bownership & insider\b|\boptions trading\b|'
    r'\b13[df]\b|\bstock holdings in\b|\bdepository receipt\b|'
    # FR: сторінки котирувань/графіків/інсайдерських угод/консенсусу аналітиків
    r'cours de l[\'’]action|cours actions?|graphique d[\'’]analyse|analyse technique|'
    r'consensus des analystes|transactions? d[\'’]initi[ée]s|'
    # PT: сторінки котирувань/графіків
    r'an[áa]lise t[ée]cnica|cota[çc][ãa]o da a[çc][ãa]o',
    re.IGNORECASE,
)
# Маркери інституційних тримачів (фондів/радників) — щоб відрізнити filings
# "X LLC купив акції" від СПРАВЖНЬОГО M&A виробника (JBS, Cargill тощо).
FUND_MARKER_RE = re.compile(
    r'\b(?:llc|l\.?\s?p\.?|lp|capital|advisers|advisors|partners|management|'
    r'investments?|asset management|wealth management|funds?|securities|'
    r'financial group|retirement system|pension|bank|mellon)\b',
    re.IGNORECASE,
)
OWNERSHIP_RE = re.compile(
    r'\b(?:buys?|sells?|bought|sold|purchas\w+|acquires?|reduces?|trims?|boosts?|'
    r'raises?|lowers?|lifts?|cuts?|increases?|decreases?|takes?|holds?)\b.{0,40}?'
    r'\b(?:shares?|stake|position|holdings)\b',
    re.IGNORECASE,
)
# Пасивний стан filings ("$TSN Shares Sold by X", "Stake Boosted by Y") —
# MarketBeat формулює саме так, тому активного OWNERSHIP_RE недостатньо.
PASSIVE_OWNERSHIP_RE = re.compile(
    r'\b(?:shares?|stake|position|holdings)\b.{0,30}?'
    r'\b(?:sold|bought|purchased|acquired|boosted|raised|lowered|reduced|'
    r'trimmed|cut|lifted|increased|decreased)\b',
    re.IGNORECASE,
)
BUY_SHARES_RE = re.compile(
    r'\b(?:buys?|sells?|bought|sold|purchas\w+)\b.{0,25}?\bshares of\b',
    re.IGNORECASE,
)
DOLLAR_HOLDINGS_RE = re.compile(
    r'\$[\d.,]+\s*(?:million|billion|thousand)\b.{0,40}?'
    r'\b(?:holdings|position|stake|shares)\b'
    r'|\bhas\b.{0,20}?\$[\d.,]+\s*(?:million|billion)\b',
    re.IGNORECASE,
)
# "Fund X invests $N million in <company>" — filing без слів shares/stake/holdings.
# Спрацьовує лише разом із фонд-маркером, тому "Tyson invests $200M in new plant"
# (капітальні інвестиції самої компанії) не зачіпається — це операційна новина.
INVESTS_RE = re.compile(
    r'\binvests?\b.{0,20}?\$[\d.,]+\s*(?:million|billion|thousand)?\b',
    re.IGNORECASE,
)


# Тактичне B2C-промо (розіграші/сувеніри) — конкуренту не цінне (на відміну від
# стратегічного маркетингу: ребрендинг, новий канал, велика спонсорська угода).
PROMO_RE = re.compile(
    r"\bsortei[oa]s?\b|\bsortei[a-z]+\b|vai sortear|\bsweepstakes?\b|\bgiveaways?\b|"
    r"\braffle\b|\bwin\b.{0,20}\btickets?\b|enter to win|colecion[áa]vel|"
    r"\bbrinde\b|pote colecion|season tickets? giveaway|"
    r"kits? exclusivos?|promo[çc][ãa]o com|combina promo|dia da lasanha|"
    # FR: конкурси/розіграші
    r"gagnez|[àa] gagner|jeu[\s-]?concours|tirage au sort|remporte[rz]",
    re.IGNORECASE,
)


def is_market_noise_title(title: str) -> bool:
    """True для біржового/сторінкового шуму, що не є бізнес-новиною конкурента:
    сторінки котирувань, форуми, ADR/BDR-лістинги, а також інституційні filings
    ("X LLC купив/продав акції", "$N million holdings", 13F). Справжні угоди M&A
    виробників (без фонд-маркерів у назві) не зачіпаються."""
    if not title:
        return False
    if STOP_PAGE_RE.search(title):
        return True
    if PROMO_RE.search(title):
        return True
    if BUY_SHARES_RE.search(title):
        return True
    if DOLLAR_HOLDINGS_RE.search(title):
        return True
    if INVESTS_RE.search(title) and FUND_MARKER_RE.search(title):
        return True
    if (OWNERSHIP_RE.search(title) or PASSIVE_OWNERSHIP_RE.search(title)) and FUND_MARKER_RE.search(title):
        return True
    return False


def compute_relevance(entity: dict, title_l: str) -> str:
    # висока: пряме ім'я сутності (не JBS-контекст) в заголовку
    direct_hit_in_title = any(re.search(p, title_l) for p in entity["keywords"])
    if entity.get("requires_context"):
        # Це JBS-рядок — за визначенням опосередкована відносно PPC
        return "низька" if not direct_hit_in_title else "середня"
    if direct_hit_in_title:
        return "висока"
    return "середня"


def collect_competitor(cfg: dict, producer_key: str, days: int) -> list[dict]:
    comp = COMPETITORS[producer_key]
    feeds = rss.read_feed_list(path(cfg, "feeds/" + comp["feeds_file"]))
    now = rss.now_utc()
    cutoff = now - dt.timedelta(days=days)
    seen_keys, seen_title_keys, out = set(), set(), []

    for feed in feeds:
        _, entries = rss.fetch(feed)
        for e in entries:
            link, title, summary = e["link"], e["title"], e["summary"]
            if not link:
                continue
            if is_stale_earnings_title(title, now) or is_market_noise_title(title):
                continue
            pub = e["pub"]
            if pub and pub < cutoff:
                continue
            full_text = f"{title} {summary}"
            text_l = full_text.lower()
            matched = match_entities(text_l, comp["entities"])
            if not matched:
                continue  # не про жодну з наших сутностей
            key = rss.canonicalize_url(link)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            event_category = classify_event_category(text_l)
            lang = detect(full_text) if full_text else "unknown"
            norm_title = re.sub(r"\W+", " ", title.lower()).strip()
            for ent in matched:  # одна новина може стосуватись кількох сутностей
                tkey = (ent["name"], norm_title)
                if tkey in seen_title_keys:
                    continue
                seen_title_keys.add(tkey)
                relevance = compute_relevance(ent, title.lower())
                out.append({
                    "date_published_utc": pub.strftime("%Y-%m-%d %H:%M:%S") if pub else "",
                    "source": e["source"], "lang_detected": lang,
                    "title_original": title, "summary_original": summary,
                    "url": link, "url_canonical": key,
                    "entity": ent["name"], "ticker": ent.get("ticker", ""),
                    "parent_company": ent.get("parent_company", ""), "entity_country": ent.get("country", ""),
                    "event_category": event_category, "relevance": relevance,
                    "ai_score": RELEVANCE_SCORE_MAP.get(relevance, 3),
                    "ai_domain": DOMAIN_LABELS.get(producer_key, comp.get("holding", comp["display_name"])),
                    "ai_category": "", "ai_country": "", "ai_commodity": "",
                    "producer": producer_key,
                })

    before = len(out)
    out = fuzzy_dedup(out)
    if before != len(out):
        log(f"Fuzzy-дедуплікація синдикації: {before} → {len(out)} рядків")
    out.sort(key=lambda x: x["date_published_utc"], reverse=True)
    log(f"{producer_key}: {len(out)} новин")
    return out


TRANSLATE_SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "integer"}, "title_uk": {"type": "string"}, "summary_uk": {"type": "string"}},
        "required": ["id", "title_uk", "summary_uk"], "additionalProperties": False}}},
    "required": ["items"], "additionalProperties": False,
}


def translate(llm, rows: list[dict], batch_size: int = 20):
    """Заповнює title_uk/summary_uk; як і раніше, ai_summary = заголовок, ai_detailed = опис."""
    todo = [r for r in rows if r.get("lang_detected") != "uk"]
    for r in rows:
        if r.get("lang_detected") == "uk":
            r["title_uk"], r["summary_uk"] = r["title_original"], r["summary_original"]
    system = "Ти — перекладач новин. Відповідай ТІЛЬКИ валідним JSON."
    for start in range(0, len(todo), batch_size):
        batch = todo[start:start + batch_size]
        lines = [f"{i}. Заголовок: {r['title_original'][:500]}\n   Опис: {r['summary_original'][:500]}"
                 for i, r in enumerate(batch)]
        try:
            data = llm.json(system, prompts.render("translate", articles="\n\n".join(lines)),
                            max_tokens=min(len(batch) * 400, 8192), schema=TRANSLATE_SCHEMA, label="переклад")
            by_id = {int(x["id"]): x for x in data.get("items", [])}
        except LLMError:
            by_id = {}
        for i, r in enumerate(batch):
            x = by_id.get(i, {})
            r["title_uk"] = x.get("title_uk") or r["title_original"]
            r["summary_uk"] = x.get("summary_uk") or r["summary_original"]
    for r in rows:
        r["ai_summary"] = r.get("title_uk", "")     # без AI-переказу — переклад заголовка
        r["ai_detailed"] = r.get("summary_uk", "")  # оригінальний (перекладений) RSS-опис
    return rows


def collect_all(llm, cfg: dict) -> dict[str, list[dict]]:
    c = cfg["competitors"]
    result = {}
    for key in c["publish"]:
        rows = collect_competitor(cfg, key, int(c["days"]))
        result[key] = translate(llm, rows)
    return result
