"""HUMAN-AI calisan demo baslatıcı.

1) Dataset + hata enjeksiyonu
2) Yeterli refaktor yoksa ilk N kodu 3 LLM ile uretir
3) Anket sunucusunu acar

Kullanim:
    python demo.py
    python demo.py --limit 10
    python demo.py --skip-refactor
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
EXPERIMENTS = os.path.join(ROOT, "experiments")
RAW = os.path.join(ROOT, "data", "raw_repos", "selected_dataset.json")
REFACTORED = os.path.join(ROOT, "data", "refactored", "refactored_dataset.json")
MIN_READY = 5


def run(cmd: list[str]) -> None:
    print("\n>>", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def count_ready() -> tuple[int, int]:
    if not os.path.exists(REFACTORED):
        return 0, 0
    items = json.load(open(REFACTORED, encoding="utf-8"))
    ready = 0
    for item in items:
        ref = item.get("refactored", {}) or {}
        llm = sum(1 for name in ("chatgpt", "groq", "gemini") if ref.get(name))
        src = item.get("code_for_llm") or item.get("original_code")
        if llm >= 2 and src:
            ready += 1
    return ready, len(items)


def main() -> None:
    parser = argparse.ArgumentParser(description="HUMAN-AI demo")
    parser.add_argument("--limit", type=int, default=15, help="Demo icin refaktor edilecek kod sayisi")
    parser.add_argument("--skip-refactor", action="store_true", help="Mevcut refaktor verisiyle devam et")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    py = sys.executable
    print("=" * 50)
    print("HUMAN-AI DEMO")
    print("=" * 50)

    run([py, os.path.join(EXPERIMENTS, "run_pipeline.py")])

    ready, total = count_ready()
    print(f"\nHazir anket kodu: {ready}/{total}")

    if not args.skip_refactor and ready < MIN_READY:
        print(f"\nYeterli refaktor yok (min {MIN_READY}). Ilk {args.limit} kod uretiliyor...")
        run([
            py,
            os.path.join(EXPERIMENTS, "refactor_pipeline.py"),
            "--limit", str(args.limit),
            "--force",
        ])
        ready, total = count_ready()
        print(f"\nGuncel hazir kod: {ready}/{total}")

    if ready == 0:
        print("\nHATA: Anket icin hazir kod yok. API key'leri kontrol edin.")
        sys.exit(1)

    print("\n" + "=" * 50)
    print(f"Anket: http://127.0.0.1:{args.port}")
    print("Durdurmak icin Ctrl+C")
    print("=" * 50 + "\n")

    env = os.environ.copy()
    env["FLASK_APP"] = "survey_app"
    subprocess.call(
        [py, os.path.join(ROOT, "app", "survey_app.py")],
        cwd=ROOT,
        env=env,
    )


if __name__ == "__main__":
    main()
