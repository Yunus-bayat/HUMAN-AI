"""Refactor all study codes through the CodeBridge (ChatGPT / Groq / Gemini)."""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from code_bridge import CodeBridge, DEFAULT_PROVIDERS


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM kod erisim koprusu + refaktor")
    parser.add_argument("--limit", type=int, default=0, help="Sadece ilk N kod (0 = hepsi)")
    parser.add_argument("--force", action="store_true", help="Mevcut ciktilari yeniden uret")
    parser.add_argument(
        "--providers",
        default=",".join(DEFAULT_PROVIDERS),
        help="Virgulle ayrilmis provider listesi",
    )
    args = parser.parse_args()

    providers = [p.strip() for p in args.providers.split(",") if p.strip()]
    bridge = CodeBridge(providers=providers)
    results = bridge.run(limit=args.limit, force=args.force)

    ok = sum(
        1
        for row in results
        if all(row.get("refactored", {}).get(name) for name in providers)
    )
    partial = sum(1 for row in results if row.get("refactored"))
    print(
        f"Bitti. Tam ({'+'.join(providers)}): {ok}/{len(results)} | "
        f"En az 1 provider: {partial}/{len(results)} -> {bridge.output_path}"
    )


if __name__ == "__main__":
    main()
