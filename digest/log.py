# -*- coding: utf-8 -*-
import datetime as dt
import sys

try:  # Windows-консоль може бути cp1251 — не падати на кирилиці/діакритиці
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def log(msg: str):
    print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)
