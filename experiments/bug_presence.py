"""Detect whether a survey choice still carries an injected semantic bug."""

from __future__ import annotations

import difflib
from typing import Any


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


def summarize_buggy_choices(
    answers: list[dict[str, Any]], items_by_id: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Aggregate buggy picks for post-survey debrief."""
    picks: list[dict[str, Any]] = []
    for row in answers:
        code_id = row.get("code_id")
        choice = row.get("chosen_source")
        if not code_id or not choice:
            continue
        item = items_by_id.get(code_id)
        if not item or not item.get("has_injected_bug"):
            continue
        had_bug = row.get("chosen_had_bug")
        if had_bug is None:
            had_bug = choice_still_has_bug(item, choice)
        if not had_bug:
            continue
        picks.append({
            "code_id": code_id,
            "chosen_source": choice,
            "question_number": row.get("question_number"),
        })

    llm_picks = [p for p in picks if p["chosen_source"] != "original"]
    source_picks = [p for p in picks if p["chosen_source"] == "original"]
    return {
        "buggy_pick_count": len(picks),
        "llm_buggy_pick_count": len(llm_picks),
        "source_buggy_pick_count": len(source_picks),
        "picks": picks,
        "show_debrief": len(picks) > 0,
    }
