# -*- coding: utf-8 -*-
"""Єдина точка звернення до AI. Провайдер обирається в .env (LLM_PROVIDER):
  anthropic — Claude (за замовчуванням)
  openai    — OpenAI API
  azure     — Azure OpenAI
Решта коду викликає лише LLM.json(...) і не знає, який провайдер працює."""
import json
import os
import time

from .log import log


THINKING_HEADROOM = 4000  # токенів на роздуми моделі понад ліміт відповіді (лише коли задано effort)


class LLMError(Exception):
    pass


class Usage:
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.calls = 0

    def add(self, inp: int, out: int):
        self.input_tokens += inp or 0
        self.output_tokens += out or 0
        self.calls += 1

    def __str__(self):
        return f"{self.calls} викликів · {self.input_tokens:,} вхідних / {self.output_tokens:,} вихідних токенів"


def _extract_json(text: str):
    """Для відповідей без схеми: беремо перший JSON-об'єкт/масив із тексту."""
    text = text.strip()
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise ValueError("у відповіді немає JSON")
    start = min(starts)
    end = max(text.rfind("}"), text.rfind("]")) + 1
    return json.loads(text[start:end])


class LLM:
    def __init__(self, cfg: dict):
        c = cfg["llm"]
        self.provider = c["provider"]
        self.model = c["model"]
        self.pause = float(c.get("pause_between_calls", 0))
        self.effort = str(c.get("effort") or "").strip()
        self.usage = Usage()
        timeout = float(c.get("timeout_seconds", 180))
        key = c["api_key"]

        if self.provider == "anthropic":
            import anthropic
            self._anthropic = anthropic
            key = key or os.environ.get("ANTHROPIC_API_KEY", "")
            if not key:
                raise LLMError("Не задано LLM_API_KEY у .env")
            # max_retries=1: власний цикл повторів нижче; два стеки повторів
            # множили б оплачені генерації.
            self.client = anthropic.Anthropic(api_key=key, timeout=timeout, max_retries=1)
        elif self.provider in ("openai", "azure"):
            try:
                import openai
            except ImportError as e:
                raise LLMError("Для openai/azure встановіть пакет: pip install openai==2.54.0") from e
            if not key:
                raise LLMError("Не задано LLM_API_KEY у .env")
            if self.provider == "openai":
                self.client = openai.OpenAI(api_key=key, timeout=timeout, max_retries=1)
            else:
                if not c["azure_endpoint"]:
                    raise LLMError("Для azure задайте AZURE_OPENAI_ENDPOINT у .env")
                self.client = openai.AzureOpenAI(api_key=key, azure_endpoint=c["azure_endpoint"],
                                                 api_version=c["azure_api_version"],
                                                 timeout=timeout, max_retries=1)
        else:
            raise LLMError(f"Невідомий LLM_PROVIDER: {self.provider}")

    # ------------------------------------------------------------------ public
    def json(self, system: str, prompt: str, max_tokens: int, schema: dict | None = None,
             attempts: int = 3, label: str = ""):
        """Повертає розібраний JSON. schema — JSON Schema об'єкта (структурована відповідь);
        без schema модель відповідає текстом, з якого ми дістаємо JSON."""
        last = None
        for attempt in range(1, attempts + 1):
            try:
                text = self._call(system, prompt, max_tokens, schema)
                data = json.loads(text) if schema else _extract_json(text)
                if self.pause:
                    time.sleep(self.pause)
                return data
            except Exception as e:  # noqa: BLE001 — логуємо будь-яку причину і пробуємо ще раз
                last = e
                wait = 60 if self._is_rate_limit(e) else 5
                log(f"    [AI{(' ' + label) if label else ''}] помилка (спроба {attempt}/{attempts}): {e}")
                if attempt < attempts:
                    time.sleep(wait)
        raise LLMError(str(last))

    # ------------------------------------------------------------------ providers
    def _call(self, system, prompt, max_tokens, schema):
        if self.provider == "anthropic":
            output_config = {}
            if schema:
                output_config["format"] = {"type": "json_schema", "schema": schema}
            if self.effort:
                # роздуми моделі входять у ліміт відповіді — даємо їм окремий запас
                output_config["effort"] = self.effort
                max_tokens += THINKING_HEADROOM
            kwargs = dict(model=self.model, max_tokens=max_tokens, system=system,
                          messages=[{"role": "user", "content": prompt}])
            if output_config:
                kwargs["output_config"] = output_config
            resp = self.client.messages.create(**kwargs)
            self.usage.add(resp.usage.input_tokens, resp.usage.output_tokens)
            if resp.stop_reason == "max_tokens":
                raise ValueError("відповідь обрізана (max_tokens)")
            if resp.stop_reason == "refusal":
                raise ValueError("модель відмовилась відповідати")
            return next(b.text for b in resp.content if b.type == "text")

        # openai / azure
        messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        if schema:
            fmt = {"type": "json_schema", "json_schema": {"name": "result", "schema": schema, "strict": True}}
        else:
            fmt = {"type": "json_object"}
        resp = self.client.chat.completions.create(model=self.model, messages=messages,
                                                   max_completion_tokens=max_tokens, response_format=fmt)
        u = resp.usage
        self.usage.add(getattr(u, "prompt_tokens", 0), getattr(u, "completion_tokens", 0))
        choice = resp.choices[0]
        if choice.finish_reason == "length":
            raise ValueError("відповідь обрізана (max_tokens)")
        return choice.message.content or ""

    def _is_rate_limit(self, e) -> bool:
        if self.provider == "anthropic":
            return isinstance(e, self._anthropic.RateLimitError)
        return type(e).__name__ == "RateLimitError"
