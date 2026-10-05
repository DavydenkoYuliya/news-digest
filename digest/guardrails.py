# -*- coding: utf-8 -*-
"""Запобіжники для AI-довідок: жодних посилань на неіснуючі новини і жодних чисел, яких немає в джерелі.
Числа перевіряються проти ОРИГІНАЛЬНОГО тексту новини (заголовок + опис RSS), а не проти AI-резюме,
бо саме в AI-резюме траплялися вигадані числа (напр. «10–14 днів», «2024» замість «цього літа»)."""
import re

_DIGITS = re.compile(r"\d+")


def digit_groups(text: str) -> set[str]:
    """Групи цифр без провідних нулів: «4,12 млрд» → {"4", "12"}; «9.13%» → {"9", "13"}."""
    return {g.lstrip("0") or "0" for g in _DIGITS.findall(text or "")}


# Числа, написані в джерелі словами («six-year low», «four months», «seis meses»), теж рахуються.
_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30, "fifty": 50,
    "hundred": 100, "thousand": 1000, "half": 50, "double": 2, "triple": 3, "dozen": 12,
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
    "oito": 8, "nove": 9, "dez": 10, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "sept": 7,
    "huit": 8, "neuf": 9, "dix": 10,
}
_WORD_RE = re.compile(r"\b(" + "|".join(sorted(_WORDS, key=len, reverse=True)) + r")(?=\b|-)", re.IGNORECASE)


def source_text(item: dict) -> str:
    return f"{item.get('title_original', '')} {item.get('summary_original', '')}"


def source_numbers(text: str) -> set[str]:
    words = {str(_WORDS[w.lower()]) for w in _WORD_RE.findall(text or "")}
    return digit_groups(text) | words


def unsupported_numbers(claim: str, sources: list[dict]) -> set[str]:
    available = set()
    for s in sources:
        available |= source_numbers(source_text(s))
    return digit_groups(claim) - available


# Валюти: у твердженні можуть бути лише ті, що є в джерелі (€85 не має стати $85).
# R$ (бразильський реал) прибираємо першим, щоб його «$» не зарахувався як долар.
_CURRENCIES = {
    "BRL": [r"R\$", r"\bBRL\b", r"\breais\b", r"\breal\b", r"\bреал(?:и|ів|а)?\b"],
    "USD": [r"\$", r"\bUSD\b", r"dollar", r"\bдолар", r"\bдол\."],
    "EUR": [r"€", r"\bEUR\b", r"\beuros?\b", r"\bєвро\b"],
    "GBP": [r"£", r"\bGBP\b", r"\bpounds?\b", r"sterling", r"\bфунт(?:и|ів|а)?\b"],
    "UAH": [r"₴", r"\bUAH\b", r"hryvni?a", r"гривн", r"\bгрн\b"],
    "CNY": [r"¥", r"\bCNY\b", r"\byuan\b", r"\bюан(?:ь|і|ів|я)?\b"],
}
_CURRENCY_RE = {code: re.compile("|".join(p), re.IGNORECASE) for code, p in _CURRENCIES.items()}


def currencies(text: str) -> set[str]:
    found, rest = set(), text or ""
    for code, rx in _CURRENCY_RE.items():  # порядок важливий: BRL перед USD
        if rx.search(rest):
            found.add(code)
            rest = rx.sub(" ", rest)
    return found


def unsupported_currencies(claim: str, sources: list[dict]) -> set[str]:
    available = set()
    for s in sources:
        available |= currencies(source_text(s))
    return currencies(claim) - available


def clean_refs(refs, allowed: set[int]) -> list[int]:
    out = []
    for r in refs or []:
        try:
            r = int(r)
        except (TypeError, ValueError):
            continue
        if r in allowed and r not in out:
            out.append(r)
    return out
