"""Inject subtle semantic bugs into exactly 20 study codes.

Clean originals stay in `original_code`.
LLMs receive `code_for_llm` (buggy for the selected 20, clean otherwise).
"""

from __future__ import annotations

import hashlib
import random
import re
from typing import Any

BUG_SEED = 42
BUG_COUNT = 20


def _stable_pick_ids(items: list[dict[str, Any]], count: int = BUG_COUNT) -> list[str]:
    ids = [item["id"] for item in items]
    rng = random.Random(BUG_SEED)
    if len(ids) <= count:
        return sorted(ids)
    return sorted(rng.sample(ids, count))


def _bug_tag(code_id: str) -> str:
    digest = hashlib.sha1(f"{BUG_SEED}:{code_id}".encode("utf-8")).hexdigest()
    return digest[:8]


def _inject_off_by_one_loop(code: str) -> tuple[str, str]:
    """Change `i < n` to `i <= n` in a for-loop (classic off-by-one)."""
    pattern = r"for\s*\(\s*int\s+(\w+)\s*=\s*0\s*;\s*\1\s*<\s*([^;]+);\s*\1\+\+\s*\)"
    match = re.search(pattern, code)
    if not match:
        return code, ""
    old = match.group(0)
    new = old.replace(f"{match.group(1)} < {match.group(2)}", f"{match.group(1)} <= {match.group(2)}", 1)
    return code.replace(old, new, 1), "off_by_one_loop"


def _inject_wrong_comparison(code: str) -> tuple[str, str]:
    """Flip a `<` comparison used in search/sort logic."""
    for old, new in ((" < ", " > "), (" <= ", " >= "), (" > ", " < "), (" >= ", " <= ")):
        if old in code:
            return code.replace(old, new, 1), "wrong_comparison"
    return code, ""


def _inject_return_sentinel(code: str) -> tuple[str, str]:
    """Change `return -1` to `return 0` (false success / wrong index)."""
    if "return -1" in code:
        return code.replace("return -1", "return 0", 1), "wrong_return_sentinel"
    if "return -1;" in code:
        return code.replace("return -1;", "return 0;", 1), "wrong_return_sentinel"
    return code, ""


def _inject_invert_condition(code: str) -> tuple[str, str]:
    """Invert a boolean condition in an if statement."""
    pattern = r"if\s*\(([^)]+)\)"
    match = re.search(pattern, code)
    if not match:
        return code, ""
    cond = match.group(1).strip()
    if cond.startswith("!"):
        inverted = cond[1:].strip()
        if inverted.startswith("(") and inverted.endswith(")"):
            inverted = inverted[1:-1]
    else:
        inverted = f"!({cond})"
    old = match.group(0)
    new = f"if ({inverted})"
    return code.replace(old, new, 1), "inverted_condition"


def _inject_arithmetic_flip(code: str) -> tuple[str, str]:
    """Flip a mid-index / arithmetic expression sign."""
    if " + " in code:
        return code.replace(" + ", " - ", 1), "arithmetic_flip"
    if " - " in code:
        return code.replace(" - ", " + ", 1), "arithmetic_flip"
    return code, ""


INJECTORS = (
    _inject_off_by_one_loop,
    _inject_wrong_comparison,
    _inject_return_sentinel,
    _inject_invert_condition,
    _inject_arithmetic_flip,
)


def inject_bug(code: str, code_id: str) -> dict[str, Any]:
    """Apply the first successful injector for this code id."""
    tag = _bug_tag(code_id)
    start = int(tag[:2], 16) % len(INJECTORS)
    ordered = INJECTORS[start:] + INJECTORS[:start]

    for injector in ordered:
        buggy, bug_type = injector(code)
        if bug_type and buggy != code:
            return {
                "has_injected_bug": True,
                "bug_type": bug_type,
                "bug_id": f"{code_id}-{tag}",
                "bug_description": (
                    f"Subtle semantic bug ({bug_type}) injected for trust measurement. "
                    "Public signatures kept; observable behavior changed."
                ),
                "code_for_llm": buggy,
            }

    # Fallback: force a compiling semantic change that always differs.
    fallback = code.replace("return -1", "return 0", 1)
    if fallback == code:
        fallback = code.replace("return true", "return false", 1)
    if fallback == code and "++" in code:
        fallback = code.replace("++", "--", 1)
    if fallback == code and " % " in code:
        # e.g. GCD: a % b  ->  b % a
        fallback = code.replace("a % b", "b % a", 1)
    if fallback == code and " != " in code:
        fallback = code.replace(" != ", " == ", 1)
    if fallback == code and " == " in code:
        fallback = code.replace(" == ", " != ", 1)
    if fallback == code:
        # Last resort: negate first returned identifier expression if present
        fallback = re.sub(
            r"return\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;",
            r"return -\1;",
            code,
            count=1,
        )
    if fallback == code:
        raise RuntimeError(f"Bug inject edilemedi: {code_id}")

    return {
        "has_injected_bug": True,
        "bug_type": "fallback_mutation",
        "bug_id": f"{code_id}-{tag}",
        "bug_description": "Fallback mutation applied for trust measurement.",
        "code_for_llm": fallback,
    }


def prepare_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return study-ready items: clean original + code_for_llm (+ bug meta)."""
    buggy_ids = set(_stable_pick_ids(items, BUG_COUNT))
    prepared: list[dict[str, Any]] = []

    for item in items:
        row = dict(item)
        original = item["original_code"]
        row["original_code"] = original

        if item["id"] in buggy_ids:
            meta = inject_bug(original, item["id"])
            row.update(meta)
        else:
            row["has_injected_bug"] = False
            row["bug_type"] = None
            row["bug_id"] = None
            row["bug_description"] = None
            row["code_for_llm"] = original

        prepared.append(row)

    return prepared


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    buggy = [i for i in items if i.get("has_injected_bug")]
    by_type: dict[str, int] = {}
    for item in buggy:
        by_type[item.get("bug_type") or "unknown"] = by_type.get(item.get("bug_type") or "unknown", 0) + 1
    return {
        "total": len(items),
        "buggy": len(buggy),
        "clean": len(items) - len(buggy),
        "buggy_ids": [i["id"] for i in buggy],
        "by_type": by_type,
    }
