"""52 kod icin benzerlik/konu gruplari (HUMAN-AI anket filtreleme)."""

from __future__ import annotations

# category_id -> meta
CATEGORIES: dict[str, dict[str, str]] = {
    "search": {
        "label": "Arama ve Filtreleme",
        "topic": "arama ve filtreleme",
    },
    "sort": {
        "label": "Sıralama ve Önceliklendirme",
        "topic": "sıralama algoritması",
    },
    "string": {
        "label": "Metin ve Dize İşlemleri",
        "topic": "metin işleme",
    },
    "data_structures": {
        "label": "Veri Yapıları",
        "topic": "veri yapısı",
    },
    "finance": {
        "label": "Finans ve Hesaplama",
        "topic": "finans ve hesaplama",
    },
    "validation": {
        "label": "Doğrulama ve Güvenlik",
        "topic": "doğrulama ve güvenlik",
    },
    "parsing": {
        "label": "Ayrıştırma ve Veri Yolu",
        "topic": "ayrıştırma ve veri yolu",
    },
    "graph_tree": {
        "label": "Graf ve Ağaç",
        "topic": "graf ve ağaç",
    },
    "scheduling": {
        "label": "Zaman ve İş Akışı",
        "topic": "zaman ve iş akışı",
    },
    "array_stats": {
        "label": "Dizi ve İstatistik",
        "topic": "dizi ve istatistik",
    },
    "business": {
        "label": "İş Mantığı",
        "topic": "iş mantığı",
    },
    "encoding": {
        "label": "Kodlama ve Sıkıştırma",
        "topic": "kodlama ve sıkıştırma",
    },
}

# code_id -> category_id
CODE_CATEGORY: dict[str, str] = {
    "code_01": "search",
    "code_02": "sort",
    "code_03": "string",
    "code_04": "data_structures",
    "code_05": "finance",
    "code_06": "parsing",
    "code_07": "graph_tree",
    "code_08": "validation",
    "code_09": "scheduling",
    "code_10": "string",
    "code_11": "business",
    "code_12": "graph_tree",
    "code_13": "finance",
    "code_14": "string",
    "code_15": "data_structures",
    "code_16": "scheduling",
    "code_17": "array_stats",
    "code_18": "parsing",
    "code_19": "data_structures",
    "code_20": "scheduling",
    "code_21": "array_stats",
    "code_22": "validation",
    "code_23": "finance",
    "code_24": "string",
    "code_25": "sort",
    "code_26": "array_stats",
    "code_27": "search",
    "code_28": "encoding",
    "code_29": "finance",
    "code_30": "array_stats",
    "code_31": "string",
    "code_32": "business",
    "code_33": "encoding",
    "code_34": "array_stats",
    "code_35": "business",
    "code_36": "string",
    "code_37": "finance",
    "code_38": "parsing",
    "code_39": "validation",
    "code_40": "encoding",
    "code_41": "parsing",
    "code_42": "business",
    "code_43": "search",
    "code_44": "finance",
    "code_45": "scheduling",
    "code_46": "search",
    "code_47": "data_structures",
    "code_48": "array_stats",
    "code_49": "array_stats",
    "code_50": "scheduling",
    "code_51": "sort",
    "code_52": "graph_tree",
}

MIN_CATEGORY_OPTIONS = 3
MAX_OPTIONS_PER_SURVEY = 4


def category_for(code_id: str) -> str:
    return CODE_CATEGORY.get(code_id, "business")


def build_four_way_survey_prompt(item: dict) -> str:
    """Backward-compatible alias; prefer survey_i18n.build_survey_prompt."""
    cid = item.get("category") or category_for(item["id"])
    meta = CATEGORIES[cid]
    topic = meta.get("topic", meta["label"].lower())
    return (
        f"Aşağıda {topic} kodunun beş versiyonu sunuluyor: kaynak kod ile dört yapay zeka "
        f"sürümü (ChatGPT, Groq, Google Gemini, Claude). "
        f"Lütfen en güvenilir bulduğunuzu seçin."
    )


def attach_category(item: dict) -> dict:
    """Dataset satirina category alanlarini ekle."""
    cid = category_for(item["id"])
    meta = CATEGORIES[cid]
    row = dict(item)
    row["category"] = cid
    row["category_label"] = meta["label"]
    row["category_prompt"] = meta.get("topic", meta["label"])
    return row


def group_by_category(items: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {k: [] for k in CATEGORIES}
    for item in items:
        cid = item.get("category") or category_for(item["id"])
        groups.setdefault(cid, []).append(item)
    return groups


def categories_ready(items: list[dict]) -> dict[str, int]:
    """Anket icin yeterli kodu olan kategoriler."""
    grouped = group_by_category(items)
    return {
        cid: len(rows)
        for cid, rows in grouped.items()
        if len(rows) >= MIN_CATEGORY_OPTIONS
    }


def summarize_categories(items: list[dict]) -> list[dict]:
    grouped = group_by_category(items)
    out = []
    for cid, meta in CATEGORIES.items():
        rows = grouped.get(cid, [])
        out.append({
            "category": cid,
            "label": meta["label"],
            "count": len(rows),
            "ready": len(rows) >= MIN_CATEGORY_OPTIONS,
            "code_ids": [r["id"] for r in rows],
        })
    return out
