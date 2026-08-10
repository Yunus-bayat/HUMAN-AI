"""Analyze participant choices on buggy questions: did selected LLM fix the bug?

Usage:
    python experiments/analyze_buggy_choices.py
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from bug_presence import choice_still_has_bug, llm_bug_status
from results_store import get_storage_stats, load_rows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFACTORED_PATH = os.path.join(ROOT, "data", "refactored", "refactored_dataset.json")

LABELS = {
    "original": "Kaynak Kod",
    "chatgpt": "ChatGPT",
    "groq": "Groq",
    "gemini": "Gemini",
    "claude": "Claude",
}


def load_items() -> dict[str, dict]:
    with open(REFACTORED_PATH, encoding="utf-8") as f:
        return {item["id"]: item for item in json.load(f)}


def analyze(rows: list[dict], items_by_id: dict[str, dict]) -> list[dict]:
    results = []
    for row in rows:
        if not row.get("has_injected_bug"):
            continue

        code_id = row.get("code_id") or ""
        item = items_by_id.get(code_id)
        choice = row.get("chosen_source") or ""
        label = row.get("choice_label") or LABELS.get(choice, choice)

        if not item:
            fixed = None
            status = "veri_yok"
        elif choice == "original":
            fixed = False
            status = "kaynak_hatali"
        else:
            fixed = not choice_still_has_bug(item, choice)
            status = "duzeltti" if fixed else "duzeltmedi"

        results.append({
            "session": (row.get("response_id") or row.get("participant_id") or "")[:8],
            "timestamp": (row.get("timestamp") or "")[:19],
            "question": row.get("question_number"),
            "code_id": code_id,
            "description": row.get("description") or "",
            "choice": label,
            "choice_key": choice,
            "fixed": fixed,
            "status": status,
            "llm_status": llm_bug_status(item) if item else {},
        })
    return results


def print_report(results: list[dict], stats: dict) -> None:
    print("=== Hatali sorularda secim vs LLM hata duzeltme ===")
    print(
        f"Katilimci: {stats['participant_count']} | "
        f"Toplam secim: {stats['choices_count']} | "
        f"Hatali soru secimi: {len(results)}"
    )
    print()
    print(f"{'Oturum':<10} {'Soru':<5} {'Kod':<10} {'Secim':<12} {'Duzeltti mi?':<22} Tum LLM durumu")
    print("-" * 100)

    for row in results:
        if row["choice_key"] == "original":
            answer = "Hayir (Kaynak hatali)"
        elif row["fixed"] is True:
            answer = "Evet"
        elif row["fixed"] is False:
            answer = "Hayir"
        else:
            answer = "?"

        llm_parts = []
        for provider in ("chatgpt", "groq", "gemini", "claude"):
            if provider in row["llm_status"]:
                tag = "OK" if not row["llm_status"][provider] else "BUG"
                llm_parts.append(f"{provider}:{tag}")

        print(
            f"{row['session']:<10} {str(row['question']):<5} {row['code_id']:<10} "
            f"{row['choice']:<12} {answer:<22} {', '.join(llm_parts)}"
        )

    print()
    print("--- Ozet ---")
    for key, count in Counter(r["status"] for r in results).most_common():
        print(f"  {key}: {count}")

    llm_choices = [r for r in results if r["choice_key"] != "original"]
    if llm_choices:
        fixed_n = sum(1 for r in llm_choices if r["fixed"])
        pct = round(fixed_n / len(llm_choices) * 100, 1)
        print(
            f"  LLM secimlerinde duzeltme: {fixed_n}/{len(llm_choices)} ({pct}%)"
        )

    by_llm: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "fixed": 0})
    for row in llm_choices:
        key = row["choice_key"]
        by_llm[key]["total"] += 1
        if row["fixed"]:
            by_llm[key]["fixed"] += 1

    print()
    print("--- Secilen LLM bazinda (hatali sorularda) ---")
    for provider in ("chatgpt", "groq", "gemini", "claude"):
        data = by_llm[provider]
        if not data["total"]:
            continue
        pct = round(data["fixed"] / data["total"] * 100, 0)
        print(
            f"  {LABELS[provider]}: {data['fixed']}/{data['total']} secimde hatayi "
            f"duzeltmis ({pct:.0f}%)"
        )


def main() -> None:
    items = load_items()
    rows = load_rows()
    stats = get_storage_stats()
    if not rows:
        print("Kayitli cevap yok.")
        return
    results = analyze(rows, items)
    print_report(results, stats)


if __name__ == "__main__":
    main()
