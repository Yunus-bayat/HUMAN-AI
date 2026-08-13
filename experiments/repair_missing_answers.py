"""Backfill missing survey answers for abandoned sessions (1/5 answers saved).

Use when a participant started but only the first answer was persisted.
Inserts rows with mapping.backfilled=true so they can be filtered in analysis.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "app"))

from code_categories import CATEGORIES, category_for  # noqa: E402
from results_store import append_result, load_rows  # noqa: E402

REF_PATH = os.path.join(ROOT, "data", "refactored", "refactored_dataset.json")

SOURCE_LABELS = {
    "original": "Kaynak Kod",
    "gemini": "Google Gemini",
    "chatgpt": "ChatGPT",
    "groq": "Groq",
    "claude": "Claude",
}


def load_items() -> dict[str, dict]:
    with open(REF_PATH, encoding="utf-8") as f:
        return {item["id"]: item for item in json.load(f)}


def build_row(
    *,
    response_id: str,
    question_number: int,
    code_id: str,
    chosen_source: str,
    template: dict,
    timestamp: str,
) -> dict:
    item = load_items()[code_id]
    cid = item.get("category") or category_for(code_id)
    meta = CATEGORIES.get(cid, {})
    return {
        "response_id": response_id,
        "timestamp": timestamp,
        "survey_mode": template.get("survey_mode") or "five_way",
        "session_questions": int(template.get("session_questions") or 5),
        "question_number": question_number,
        "code_id": code_id,
        "description": item.get("description"),
        "category": cid,
        "category_label": meta.get("label") or item.get("category_label"),
        "choice_label": SOURCE_LABELS.get(chosen_source, chosen_source),
        "chosen_source": chosen_source,
        "has_injected_bug": bool(item.get("has_injected_bug")),
        "bug_type": item.get("bug_type"),
        "bug_id": item.get("bug_id"),
        "mapping": {
            "backfilled": True,
            "reason": "session_abandoned_after_q1",
            "note": "Q2-5 not submitted; placeholder row to complete session metadata",
        },
    }


def main() -> None:
    rows = load_rows()
    by_rid: dict[str, list[dict]] = {}
    for row in rows:
        rid = row.get("response_id")
        if rid:
            by_rid.setdefault(rid, []).append(row)

    inserted = 0
    for rid, answers in sorted(by_rid.items()):
        if len(answers) != 1 or answers[0].get("question_number") != 1:
            continue

        from results_store import SurveySessionStore

        state = SurveySessionStore().get(rid)
        if not state:
            print(f"SKIP {rid}: no session state")
            continue

        question_ids = state.get("question_ids") or []
        if len(question_ids) != 5:
            print(f"SKIP {rid}: expected 5 question ids")
            continue

        template = answers[0]
        chosen = template.get("chosen_source") or "original"
        base_ts = template.get("timestamp") or datetime.now(timezone.utc).isoformat()

        for qnum, code_id in enumerate(question_ids[1:], start=2):
            exists = any(a.get("question_number") == qnum for a in answers)
            if exists:
                continue
            row = build_row(
                response_id=rid,
                question_number=qnum,
                code_id=code_id,
                chosen_source=chosen,
                template=template,
                timestamp=base_ts,
            )
            append_result(row)
            inserted += 1
            print(f"INSERT {rid} Q{qnum} {code_id} -> {chosen}")

    print(f"Done. Inserted {inserted} backfill rows.")
    rows_after = load_rows()
    print(f"Total rows now: {len(rows_after)}")


if __name__ == "__main__":
    main()
