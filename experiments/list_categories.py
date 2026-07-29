"""52 kodun konu gruplarini listele."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from code_categories import summarize_categories

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw_repos", "selected_dataset.json")


def main() -> None:
    if not os.path.exists(RAW):
        print("Once: python experiments/run_pipeline.py")
        return
    items = json.load(open(RAW, encoding="utf-8"))
    print("HUMAN-AI kod gruplari\n" + "-" * 40)
    for row in summarize_categories(items):
        mark = "anket OK" if row["ready"] else "yetersiz"
        print(f"{row['label']}: {row['count']} kod [{mark}]")
        print(f"  id'ler: {', '.join(row['code_ids'])}")
        print()


if __name__ == "__main__":
    main()
