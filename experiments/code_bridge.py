"""Bridge between study Java codes and LLM refactor providers.

Loads prepared dataset, feeds each model the correct `code_for_llm`,
retries transient failures, and persists results incrementally.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Callable

from bug_injector import prepare_items, summarize
from llm_clients import PROVIDERS
from study_prompts import PROMPT_VERSION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(ROOT, "data", "raw_repos", "selected_dataset.json")
OUTPUT_PATH = os.path.join(ROOT, "data", "refactored", "refactored_dataset.json")

DEFAULT_PROVIDERS = ("chatgpt", "groq", "gemini")
TRANSIENT_MARKERS = (
    "429",
    "rate limit",
    "timeout",
    "temporarily",
    "unavailable",
    "503",
    "502",
    "connection",
)


class CodeBridge:
    """Single entry point: dataset -> LLM providers -> refactored JSON."""

    def __init__(
        self,
        input_path: str = RAW_PATH,
        output_path: str = OUTPUT_PATH,
        providers: tuple[str, ...] | list[str] = DEFAULT_PROVIDERS,
        max_retries: int = 2,
        pause_seconds: float = 0.7,
    ) -> None:
        self.input_path = input_path
        self.output_path = output_path
        self.providers = list(providers)
        self.max_retries = max_retries
        self.pause_seconds = pause_seconds

        for name in self.providers:
            if name not in PROVIDERS:
                raise ValueError(f"Bilinmeyen provider: {name}. Secenekler: {list(PROVIDERS)}")

    def load_raw(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(
                f"Dataset yok: {self.input_path}. Once `python experiments/run_pipeline.py` calistir."
            )
        with open(self.input_path, encoding="utf-8") as f:
            return json.load(f)

    def ensure_prepared(self, items: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        """Guarantee every item has original_code + code_for_llm (+ bug flags)."""
        source = items if items is not None else self.load_raw()
        if source and "code_for_llm" in source[0] and "has_injected_bug" in source[0]:
            prepared = source
        else:
            prepared = prepare_items(source)
            self.save_raw(prepared)
        return prepared

    def save_raw(self, items: list[dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self.input_path), exist_ok=True)
        with open(self.input_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=4, ensure_ascii=False)

    def load_existing(self) -> dict[str, dict[str, Any]]:
        if not os.path.exists(self.output_path):
            return {}
        with open(self.output_path, encoding="utf-8") as f:
            items = json.load(f)
        return {item["id"]: item for item in items}

    def save_results(self, items: list[dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        tmp_path = f"{self.output_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self.output_path)

    @staticmethod
    def code_for_provider(item: dict[str, Any]) -> str:
        """What the LLM should see."""
        return item.get("code_for_llm") or item["original_code"]

    def _call_with_retry(self, fn: Callable[[str], str], code: str, provider: str) -> str:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 2):
            try:
                return fn(code)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                message = str(exc).lower()
                retryable = any(marker in message for marker in TRANSIENT_MARKERS)
                # insufficient_quota is not worth retrying
                if "insufficient_quota" in message or not retryable:
                    raise
                if attempt > self.max_retries:
                    raise
                wait = self.pause_seconds * attempt * 2
                print(f"    [{provider}] gecici hata, {wait:.1f}s sonra tekrar ({attempt})...")
                time.sleep(wait)
        assert last_error is not None
        raise last_error

    def refactor_one(
        self,
        item: dict[str, Any],
        existing: dict[str, dict[str, Any]],
        force: bool = False,
    ) -> dict[str, Any]:
        code_id = item["id"]
        llm_code = self.code_for_provider(item)

        result = existing.get(
            code_id,
            {
                "id": code_id,
                "description": item.get("description"),
                "source_reference": item.get("source_reference"),
                "original_code": item["original_code"],
                "code_for_llm": llm_code,
                "has_injected_bug": bool(item.get("has_injected_bug")),
                "bug_type": item.get("bug_type"),
                "bug_id": item.get("bug_id"),
                "bug_description": item.get("bug_description"),
                "refactored": {},
                "errors": {},
            },
        )

        result["description"] = item.get("description")
        result["source_reference"] = item.get("source_reference")
        result["original_code"] = item["original_code"]
        result["code_for_llm"] = llm_code
        result["has_injected_bug"] = bool(item.get("has_injected_bug"))
        result["bug_type"] = item.get("bug_type")
        result["bug_id"] = item.get("bug_id")
        result["bug_description"] = item.get("bug_description")
        result.setdefault("refactored", {})
        result.setdefault("errors", {})
        result["prompt_version"] = PROMPT_VERSION

        for name in self.providers:
            if not force and result["refactored"].get(name):
                print(f"  [{code_id}] {name}: atlandi (mevcut)")
                continue
            try:
                print(f"  [{code_id}] {name}: refaktor ediliyor...")
                result["refactored"][name] = self._call_with_retry(
                    PROVIDERS[name],
                    llm_code,
                    name,
                )
                result["errors"].pop(name, None)
                time.sleep(self.pause_seconds)
            except Exception as exc:  # noqa: BLE001
                result["errors"][name] = str(exc)
                print(f"  [{code_id}] {name}: HATA -> {exc}")

        return result

    def run(self, limit: int = 0, force: bool = False) -> list[dict[str, Any]]:
        prepared = self.ensure_prepared()
        if limit > 0:
            prepared = prepared[:limit]

        info = summarize(prepared)
        print(
            f"Bridge hazir: {info['total']} kod | "
            f"hatali={info['buggy']} temiz={info['clean']} | "
            f"providers={self.providers} | prompt={PROMPT_VERSION}"
        )
        if info["buggy_ids"]:
            print(f"Hata enjekte edilen id'ler: {', '.join(info['buggy_ids'])}")

        existing = self.load_existing()
        order = {row["id"]: idx for idx, row in enumerate(self.ensure_prepared())}
        results: list[dict[str, Any]] = []

        for item in prepared:
            updated = self.refactor_one(item, existing, force=force)
            results.append(updated)
            existing[item["id"]] = updated
            ordered = sorted(existing.values(), key=lambda x: order.get(x["id"], 10_000))
            self.save_results(ordered)

        return results
