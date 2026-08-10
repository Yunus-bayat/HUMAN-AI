"""Detect whether a survey choice still carries an injected semantic bug."""

from __future__ import annotations

import difflib
from typing import Any

LLM_PROVIDERS = ("chatgpt", "groq", "gemini", "claude")


def _bug_markers(clean: str, buggy: str) -> list[str]:
    """Lines or fragments present in buggy but changed in clean source."""
    clean_lines = clean.splitlines()
    buggy_lines = buggy.splitlines()
    markers: list[str] = []
    for clean_line, buggy_line in zip(clean_lines, buggy_lines):
        if clean_line != buggy_line:
            fragment = buggy_line.strip()
            if fragment and fragment not in clean:
                markers.append(fragment)
    if len(buggy_lines) > len(clean_lines):
        for line in buggy_lines[len(clean_lines) :]:
            fragment = line.strip()
            if fragment:
                markers.append(fragment)
    # Fallback: unified diff hunks from buggy side
    if not markers:
        for line in difflib.unified_diff(
            clean.splitlines(), buggy.splitlines(), lineterm=""
        ):
            if line.startswith("+") and not line.startswith("+++"):
                fragment = line[1:].strip()
                if fragment:
                    markers.append(fragment)
    # Prefer longer markers first (more specific)
    markers.sort(key=len, reverse=True)
    seen: set[str] = set()
    unique: list[str] = []
    for marker in markers:
        if marker not in seen:
            seen.add(marker)
            unique.append(marker)
    return unique


def choice_still_has_bug(item: dict[str, Any], choice_key: str) -> bool:
    """True if the selected version likely still contains the injected bug."""
    if not item.get("has_injected_bug"):
        return False

    clean = item.get("original_code") or ""
    buggy = item.get("code_for_llm") or ""
    if not buggy:
        return False

    if choice_key == "original":
        # Survey "Kaynak Kod" shows code_for_llm (buggy input).
        return True

    chosen = (item.get("refactored") or {}).get(choice_key) or ""
    if not chosen:
        return False

    markers = _bug_markers(clean, buggy)
    if not markers:
        return chosen.strip() != clean.strip()

    return any(marker in chosen for marker in markers)


def llm_bug_status(item: dict[str, Any]) -> dict[str, bool]:
    """Per-LLM bug carry-over: True = refactored code likely still has the bug."""
    if not item.get("has_injected_bug"):
        return {}

    refactored = item.get("refactored") or {}
    status: dict[str, bool] = {}
    for provider in LLM_PROVIDERS:
        if refactored.get(provider):
            status[provider] = choice_still_has_bug(item, provider)
    return status


def summarize_session_debrief(
    answers: list[dict[str, Any]], items_by_id: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Personal debrief for the participant's 5 survey questions."""
    sorted_answers = sorted(answers, key=lambda r: int(r.get("question_number") or 0))
    all_questions: list[dict[str, Any]] = []

    for row in sorted_answers:
        code_id = row.get("code_id") or ""
        item = items_by_id.get(code_id)
        has_bug = bool(item and item.get("has_injected_bug"))
        choice = row.get("chosen_source") or ""

        llm_status = llm_bug_status(item) if item and has_bug else {}
        llm_fix: dict[str, str] = {}
        for provider in LLM_PROVIDERS:
            if has_bug and provider in llm_status:
                llm_fix[provider] = "preserved" if llm_status[provider] else "fixed"
            else:
                llm_fix[provider] = "na"

        if has_bug and item:
            had_bug = row.get("chosen_had_bug")
            if had_bug is None:
                had_bug = choice_still_has_bug(item, choice)
            user_picked_buggy = bool(had_bug)
            user_fixed = not user_picked_buggy
        else:
            user_picked_buggy = None
            user_fixed = None

        all_questions.append({
            "question_number": int(row.get("question_number") or 0),
            "description": row.get("description") or (item or {}).get("description") or code_id,
            "code_id": code_id,
            "has_injected_bug": has_bug,
            "choice_label": row.get("choice_label") or choice,
            "chosen_source": choice,
            "user_picked_buggy": user_picked_buggy,
            "user_fixed": user_fixed,
            "llm_fix": llm_fix,
            "llm_fixed": [p for p, s in llm_fix.items() if s == "fixed"],
            "llm_preserved": [p for p, s in llm_fix.items() if s == "preserved"],
        })

    buggy_questions = [q for q in all_questions if q["has_injected_bug"]]

    return {
        "total_questions": len(sorted_answers),
        "buggy_question_count": len(buggy_questions),
        "buggy_questions": buggy_questions,
        "all_questions": all_questions,
        "user_picked_buggy_count": sum(
            1 for q in buggy_questions if q["user_picked_buggy"]
        ),
        "show_debrief": len(sorted_answers) > 0,
    }


def summarize_buggy_choices(
    answers: list[dict[str, Any]], items_by_id: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Backward-compatible alias."""
    return summarize_session_debrief(answers, items_by_id)
