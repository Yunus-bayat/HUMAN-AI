"""Export curated Java dataset and inject bugs into exactly 20 codes."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from bug_injector import prepare_items, summarize
from code_categories import attach_category, summarize_categories
from dataset import SELECTED_DATASET

EXPECTED_CODE_COUNT = 52


def run_pipeline() -> None:
    print(f"Sistem calisiyor... ({len(SELECTED_DATASET)} kod)")

    if len(SELECTED_DATASET) != EXPECTED_CODE_COUNT:
        raise SystemExit(
            f"Beklenen {EXPECTED_CODE_COUNT} kod, bulunan: {len(SELECTED_DATASET)}"
        )

    prepared = [attach_category(row) for row in prepare_items(SELECTED_DATASET)]
    info = summarize(prepared)
    cat_info = summarize_categories(prepared)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(root, "data", "raw_repos", "selected_dataset.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(prepared, f, indent=4, ensure_ascii=False)

    print(f"Kaynak kodlar kaydedildi: {output_path}")
    print(
        f"Hata enjeksiyonu: {info['buggy']}/{info['total']} kod "
        f"(tipler: {info['by_type']})"
    )
    print(f"Hatali id'ler: {', '.join(info['buggy_ids'])}")
    print("\nKategori dagilimi:")
    for row in cat_info:
        mark = "OK" if row["ready"] else "yetersiz"
        print(f"  {row['label']}: {row['count']} kod [{mark}]")


if __name__ == "__main__":
    run_pipeline()
