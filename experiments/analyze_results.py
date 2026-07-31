"""Analyze blind survey choices for HUMAN-AI trust study.

Answers:
1) Which LLM was selected most?
2) How many choices trusted source code instead of any LLM?
"""

from __future__ import annotations

import os
import sys
from collections import Counter

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from results_store import load_rows

LLM_NAMES = ("chatgpt", "groq", "gemini")


def analyze(rows):
    total = len(rows)
    by_source = Counter(r.get("chosen_source") for r in rows)
    participants = {
        r.get("response_id") or r.get("participant_id")
        for r in rows
        if r.get("response_id") or r.get("participant_id")
    }

    source_count = by_source.get("original", 0)
    llm_count = sum(by_source.get(name, 0) for name in LLM_NAMES)
    llm_ranking = sorted(
        ((name, by_source.get(name, 0)) for name in LLM_NAMES),
        key=lambda x: x[1],
        reverse=True,
    )

    buggy = [r for r in rows if r.get("has_injected_bug")]
    buggy_source = sum(1 for r in buggy if r.get("chosen_source") == "original")
    buggy_llm = len(buggy) - buggy_source

    return {
        "total_choices": total,
        "participants": len(participants),
        "source_trusted": source_count,
        "source_trusted_pct": round((source_count / total) * 100, 1) if total else 0.0,
        "llm_trusted": llm_count,
        "llm_trusted_pct": round((llm_count / total) * 100, 1) if total else 0.0,
        "llm_ranking": llm_ranking,
        "most_selected_llm": llm_ranking[0][0] if llm_ranking and llm_ranking[0][1] > 0 else None,
        "buggy_set_total": len(buggy),
        "buggy_set_source": buggy_source,
        "buggy_set_llm": buggy_llm,
    }


def main() -> None:
    rows = load_rows()
    report = analyze(rows)
    print("HUMAN-AI guven analizi")
    print("-" * 40)
    print(f"Toplam secim: {report['total_choices']}")
    print(f"Katilimci: {report['participants']}")
    print()
    print("Kaynak vs LLM")
    print(
        f"  Kaynak koda guvenen secimler: "
        f"{report['source_trusted']} ({report['source_trusted_pct']}%)"
    )
    print(
        f"  LLM secimleri: "
        f"{report['llm_trusted']} ({report['llm_trusted_pct']}%)"
    )
    print()
    print("LLM siralamasi")
    for name, count in report["llm_ranking"]:
        pct = round((count / report["total_choices"]) * 100, 1) if report["total_choices"] else 0.0
        print(f"  {name}: {count} ({pct}%)")
    print(f"En cok secilen LLM: {report['most_selected_llm'] or '-'}")
    print()
    print("Hata enjekte edilmis kodlar")
    print(f"  Toplam: {report['buggy_set_total']}")
    print(f"  Kaynak tercihi: {report['buggy_set_source']}")
    print(f"  LLM tercihi: {report['buggy_set_llm']}")


if __name__ == "__main__":
    main()
