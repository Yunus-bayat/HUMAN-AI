"""Quick status check for refactored dataset readiness."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from code_categories import summarize_categories

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(ROOT, "data", "raw_repos", "selected_dataset.json")
REF_PATH = os.path.join(ROOT, "data", "refactored", "refactored_dataset.json")
PROVIDERS = ("chatgpt", "groq", "gemini", "claude")


def is_full_ready(item: dict) -> bool:
    ref = item.get("refactored") or {}
    src = item.get("code_for_llm") or item.get("original_code")
    return bool(src) and all(ref.get(name) for name in PROVIDERS)


def main() -> None:
    with open(RAW_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    with open(REF_PATH, encoding="utf-8") as f:
        ref = json.load(f)

    ref_by_id = {item["id"]: item for item in ref}
    full = [item for item in ref if is_full_ready(item)]
    errors = []
    for item in ref:
        for name, msg in (item.get("errors") or {}).items():
            errors.append(f"{item['id']} / {name}: {msg}")

    missing_ids = [item["id"] for item in raw if item["id"] not in ref_by_id]
    partial_ids = [
        item["id"]
        for item in ref
        if item["id"] in ref_by_id and not is_full_ready(item)
    ]

    print("HUMAN-AI refactor durumu")
    print("-" * 40)
    print(f"Dataset: {len(raw)} kod")
    print(f"Refactored dosyasi: {len(ref)} kayit")
    print(f"Tam hazir (5 secenek): {len(full)}/{len(raw)}")
    print(f"Eksik kayit: {len(missing_ids)}")
    print(f"Kismi kayit: {len(partial_ids)}")
    for name in PROVIDERS:
        count = sum(1 for item in ref if (item.get("refactored") or {}).get(name))
        print(f"  {name}: {count}/{len(ref)}")

    if missing_ids:
        print(f"\nRefactor dosyasinda olmayan id'ler: {', '.join(missing_ids)}")
    if partial_ids:
        print(f"\nKismi id'ler: {', '.join(partial_ids)}")
    if errors:
        print(f"\nHata kayitlari ({len(errors)}):")
        for row in errors[:10]:
            print(f"  {row}")

    ready_items = [ref_by_id[item["id"]] for item in raw if item["id"] in ref_by_id and is_full_ready(ref_by_id[item["id"]])]
    print("\nKategori hazirlik:")
    for row in summarize_categories(ready_items):
        mark = "OK" if row["ready"] else "eksik"
        print(f"  {row['label']}: {row['count']} [{mark}]")


if __name__ == "__main__":
    main()
