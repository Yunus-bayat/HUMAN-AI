"""52 kod icin benzerlik/konu gruplari (HUMAN-AI anket filtreleme)."""

from __future__ import annotations

# category_id -> meta
CATEGORIES: dict[str, dict[str, str]] = {
    "search": {
        "label": "Arama ve Filtreleme",
        "topic": "arama ve filtreleme",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM (ChatGPT, Groq, Gemini) tarafindan "
            "refaktorize edilmistir. Size uygun olan arama/filtreleme kodunu seciniz."
        ),
    },
    "sort": {
        "label": "Siralama ve Onceliklendirme",
        "topic": "siralama algoritmasi",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan siralama / onceliklendirme kodunu seciniz."
        ),
    },
    "string": {
        "label": "Metin ve String Islemleri",
        "topic": "metin isleme",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan metin isleme kodunu seciniz."
        ),
    },
    "data_structures": {
        "label": "Veri Yapilari",
        "topic": "veri yapisi",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan veri yapisi kodunu seciniz."
        ),
    },
    "finance": {
        "label": "Finans ve Hesaplama",
        "topic": "finans ve hesaplama",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan finans / hesaplama kodunu seciniz."
        ),
    },
    "validation": {
        "label": "Dogrulama ve Guvenlik",
        "topic": "dogrulama ve guvenlik",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan dogrulama / guvenlik kodunu seciniz."
        ),
    },
    "parsing": {
        "label": "Ayristirma ve Veri Yolu",
        "topic": "ayristirma ve veri yolu",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan ayristirma / yol birlestirme kodunu seciniz."
        ),
    },
    "graph_tree": {
        "label": "Graf ve Agac",
        "topic": "graf ve agac",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan graf / agac kodunu seciniz."
        ),
    },
    "scheduling": {
        "label": "Zaman ve Is Akisi",
        "topic": "zaman ve is akisi",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan zaman / is akisi kodunu seciniz."
        ),
    },
    "array_stats": {
        "label": "Dizi ve Istatistik",
        "topic": "dizi ve istatistik",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan dizi / istatistik kodunu seciniz."
        ),
    },
    "business": {
        "label": "Is Mantigi",
        "topic": "is mantigi",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan is mantigi kodunu seciniz."
        ),
    },
    "encoding": {
        "label": "Kodlama ve Sikistirma",
        "topic": "kodlama ve sikistirma",
        "survey_prompt": (
            "Asagidaki kodlar 3 farkli LLM tarafindan refaktorize edilmistir. "
            "Size uygun olan kodlama / sikistirma kodunu seciniz."
        ),
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
    """Anket ekraninda kod turune gore aciklayici metin uret."""
    cid = item.get("category") or category_for(item["id"])
    meta = CATEGORIES[cid]
    topic = meta.get("topic", meta["label"].lower())
    return (
        f"Asagida LLM'ler (ChatGPT, Groq, Gemini, Claude) tarafindan duzenlenen "
        f"{topic} kodunun bes versiyonu yer almaktadir. "
        f"Lutfen size en guvenilir geleni seciniz."
    )


def attach_category(item: dict) -> dict:
    """Dataset satirina category alanlarini ekle."""
    cid = category_for(item["id"])
    meta = CATEGORIES[cid]
    row = dict(item)
    row["category"] = cid
    row["category_label"] = meta["label"]
    row["category_prompt"] = meta["survey_prompt"]
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
