"""Anket sonuclari ve PostgreSQL durumunu kontrol et.

Kullanim:
    python experiments/check_survey_results.py

Yerel kontrol icin .env dosyasina Render External Database URL ekleyin:
    DATABASE_URL=postgresql://...@dpg-xxx.oregon-postgres.render.com/...?sslmode=require
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))
from analyze_results import analyze, load_rows  # noqa: E402
from results_store import (  # noqa: E402
    database_url,
    fetch_recent_choices,
    get_storage_stats,
    storage_backend,
)

SOURCE_LABELS = {
    "original": "Kaynak Kod",
    "gemini": "Gemini",
    "chatgpt": "ChatGPT",
    "groq": "Groq",
}


def mask_database_url(url: str | None) -> str:
    if not url:
        return "(ayarlanmadi)"
    if "@" not in url:
        return url[:24] + "..."
    prefix, hostpart = url.split("@", 1)
    user = prefix.split("//")[-1].split(":")[0] if "//" in prefix else "user"
    return f"postgresql://{user}:****@{hostpart[:48]}..."


def print_header(title: str) -> None:
    print(title)
    print("-" * 48)


def main() -> None:
    print_header("HUMAN-AI anket sonuc kontrolu")
    backend = storage_backend()
    print(f"Depolama: {backend}")
    print(f"DATABASE_URL: {mask_database_url(database_url())}")

    stats = get_storage_stats()
    print()
    print_header("Baglanti ve kayit durumu")

    if stats["database_configured"]:
        if stats["database_connected"]:
            print("PostgreSQL baglantisi: OK")
        else:
            print("PostgreSQL baglantisi: HATA")
            print(f"  {stats['database_error']}")
            print()
            print("Ipucu: Render'dan External Database URL kullanin ve sonuna")
            print("  ?sslmode=require ekleyin.")
            return
    else:
        print("Mod: yerel dosya (data/results/choices.jsonl)")
        print(f"Dosya var mi: {'evet' if stats['results_file_exists'] else 'hayir'}")

    print(f"Kayitli cevap sayisi: {stats['choices_count']}")
    print(f"Katilimci sayisi: {stats['participant_count']}")
    print(f"Tamamlayan token: {stats['completed_tokens']}")
    print(f"Aktif oturum: {stats['active_sessions']}")

    rows = load_rows()
    if not rows:
        print()
        print("Henuz kayitli cevap yok.")
        return

    report = analyze(rows)
    print()
    print_header("Guven analizi ozeti")
    print(f"Toplam secim: {report['total_choices']}")
    print(f"Katilimci: {report['participants']}")
    print(
        f"Kaynak koda guvenen: {report['source_trusted']} "
        f"({report['source_trusted_pct']}%)"
    )
    print(f"LLM secimleri: {report['llm_trusted']} ({report['llm_trusted_pct']}%)")
    print(f"En cok secilen LLM: {report['most_selected_llm'] or '-'}")

    print()
    print_header("Secenek dagilimi")
    from collections import Counter

    by_source = Counter(r.get("chosen_source") for r in rows)
    for key in ("original", "gemini", "chatgpt", "groq"):
        label = SOURCE_LABELS[key]
        count = by_source.get(key, 0)
        pct = round((count / report["total_choices"]) * 100, 1) if report["total_choices"] else 0.0
        print(f"  {label}: {count} ({pct}%)")

    recent = fetch_recent_choices(limit=8)
    if recent:
        print()
        print_header("Son kaydedilen cevaplar")
        for row in recent:
            ts = (row.get("timestamp") or "")[:19]
            q = row.get("question_number") or "?"
            code = row.get("code_id") or "-"
            choice = row.get("choice_label") or row.get("chosen_source") or "-"
            rid = (row.get("response_id") or row.get("participant_id") or "")[:8]
            print(f"  [{ts}] oturum={rid}... soru={q} kod={code} secim={choice}")

    expected = stats["participant_count"] * 5
    if stats["choices_count"] and stats["participant_count"]:
        print()
        if stats["choices_count"] >= expected:
            print("Durum: Cevaplar kaydedilmis gorunuyor.")
        else:
            print(
                "Uyari: Cevap sayisi beklenenden az olabilir "
                f"({stats['choices_count']} cevap / {stats['participant_count']} katilimci)."
            )


if __name__ == "__main__":
    main()
