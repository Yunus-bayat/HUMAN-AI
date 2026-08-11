"""Survey UI translations (Turkish / English)."""

from __future__ import annotations

SUPPORTED_LANGS = ("tr", "en")
DEFAULT_LANG = "tr"

CODE_DESCRIPTIONS_EN: dict[str, str] = {
    "code_01": "Search records by customer ID in an order list",
    "code_02": "Sort student grades with bubble sort",
    "code_03": "Normalize and validate a ticket code",
    "code_04": "Simple key-value cache (fixed capacity)",
    "code_05": "VAT-inclusive total for invoice line items",
    "code_06": "Split a CSV row into fields (simple quoted support)",
    "code_07": "Compute depth in an organization tree",
    "code_08": "Check password security rules",
    "code_09": "Check whether two meetings overlap",
    "code_10": "Score keywords in text",
    "code_11": "Increase/decrease stock and prevent negatives",
    "code_12": "One-step reachability in a friendship matrix",
    "code_13": "Calculate installment amount with interest",
    "code_14": "Generate a URL slug from a title",
    "code_15": "Fixed-size circular buffer",
    "code_16": "Convert work minutes to hours:minutes format",
    "code_17": "Simple moving average calculation",
    "code_18": "Safely merge two path segments",
    "code_19": "Remove duplicates from a list while preserving order",
    "code_20": "Exponential backoff wait duration",
    "code_21": "Row sums in a sparse matrix",
    "code_22": "Session token format validation",
    "code_23": "Apply coupon and percentage discount in sequence",
    "code_24": "Find differing indices in two text line lists",
    "code_25": "Priority job insertion (lower number first)",
    "code_26": "Check if a point is inside a rectangle",
    "code_27": "Filter log lines by severity level",
    "code_28": "Pack boolean flags into a single int",
    "code_29": "Convert raw score to letter grade",
    "code_30": "Count values exceeding threshold within a window",
    "code_31": "Strip simple tags from text",
    "code_32": "Swap shift records between two employees",
    "code_33": "Simple rolling checksum",
    "code_34": "Rotate array k steps to the right",
    "code_35": "Find an empty seat on a seat map",
    "code_36": "Convert camelCase expression to snake_case",
    "code_37": "Error rate from success/failure counts",
    "code_38": "Join tree node path segments",
    "code_39": "Check if IP address is on an allow list",
    "code_40": "Simple run-length encode",
    "code_41": "Mask an IBAN number",
    "code_42": "Consecutive hit combo score",
    "code_43": "Filter email list by domain",
    "code_44": "Temperature unit conversion",
    "code_45": "Complete workflow steps in order",
    "code_46": "Filter records by multiple fields",
    "code_47": "Move key to front in LRU list",
    "code_48": "Aggregate daily values into weekly buckets",
    "code_49": "Start/end index for pagination",
    "code_50": "Limit notification frequency (throttle)",
    "code_51": "Sort exam scores ascending with insertion sort",
    "code_52": "Count leaf nodes in a binary tree",
}

CATEGORY_LABELS_EN: dict[str, str] = {
    "search": "Search and Filtering",
    "sort": "Sorting and Prioritization",
    "string": "Text and String Operations",
    "data_structures": "Data Structures",
    "finance": "Finance and Calculation",
    "validation": "Validation and Security",
    "parsing": "Parsing and Data Paths",
    "graph_tree": "Graph and Tree",
    "scheduling": "Time and Workflow",
    "array_stats": "Array and Statistics",
    "business": "Business Logic",
    "encoding": "Encoding and Compression",
}

CATEGORY_TOPICS_EN: dict[str, str] = {
    "search": "search and filtering",
    "sort": "sorting algorithm",
    "string": "text processing",
    "data_structures": "data structure",
    "finance": "finance and calculation",
    "validation": "validation and security",
    "parsing": "parsing and data path",
    "graph_tree": "graph and tree",
    "scheduling": "time and workflow",
    "array_stats": "array and statistics",
    "business": "business logic",
    "encoding": "encoding and compression",
}

# LLM product names must stay untranslated ("Gemini" alone becomes zodiac İkizler in TR).
PROVIDER_BRAND_LABELS = {
    "chatgpt": "ChatGPT",
    "groq": "Groq",
    "gemini": "Google Gemini",
    "claude": "Claude",
}

SOURCE_LABELS = {
    "tr": {
        "original": "Kaynak Kod",
        **PROVIDER_BRAND_LABELS,
    },
    "en": {
        "original": "Source Code",
        **PROVIDER_BRAND_LABELS,
    },
}


def normalize_lang(lang: str | None) -> str:
    if lang and lang.lower() in SUPPORTED_LANGS:
        return lang.lower()
    return DEFAULT_LANG


def localized_description(item: dict, lang: str) -> str:
    if lang == "en":
        return CODE_DESCRIPTIONS_EN.get(item["id"], item.get("description", "Java code"))
    return item.get("description", "Java kodu")


def localized_category_label(category_id: str, fallback: str, lang: str) -> str:
    if lang == "en":
        return CATEGORY_LABELS_EN.get(category_id, fallback)
    return fallback


def build_survey_prompt(topic: str, lang: str) -> str:
    if lang == "en":
        return (
            f"Below are five versions of {topic} code: the source plus four "
            f"LLM-edited versions (ChatGPT, Groq, Google Gemini, Claude). "
            f"Please select the one you find most trustworthy."
        )
    return (
        f"Asagida LLM'ler (ChatGPT, Groq, Google Gemini, Claude) tarafindan duzenlenen "
        f"{topic} kodunun bes versiyonu yer almaktadir. "
        f"Lutfen size en guvenilir geleni seciniz."
    )


def _provider_label(lang: str, provider: str) -> str:
    return SOURCE_LABELS.get(normalize_lang(lang), SOURCE_LABELS["tr"]).get(
        provider, provider
    )


def _llm_fix_note(lang: str, llm_fixed: list[str], llm_preserved: list[str]) -> str:
    """Explain which LLM refactors likely fixed vs preserved the injected bug."""
    if not llm_fixed and not llm_preserved:
        return ""

    lang = normalize_lang(lang)
    fixed_labels = [_provider_label(lang, p) for p in llm_fixed]
    preserved_labels = [_provider_label(lang, p) for p in llm_preserved]

    if lang == "en":
        if llm_fixed and not llm_preserved:
            joined = ", ".join(fixed_labels)
            return (
                f"The LLM refactors ({joined}) likely corrected this bug in the source."
            )
        if llm_preserved and not llm_fixed:
            joined = ", ".join(preserved_labels)
            return (
                f"The LLM refactors ({joined}) likely still carried the bug."
            )
        fixed_part = ", ".join(fixed_labels)
        preserved_part = ", ".join(preserved_labels)
        return (
            f"LLM refactors likely fixed the bug: {fixed_part}. "
            f"Likely still buggy: {preserved_part}."
        )

    if llm_fixed and not llm_preserved:
        joined = ", ".join(fixed_labels)
        return (
            f"LLM refaktorleri ({joined}) hatali kaynaktaki hatayi "
            f"buyuk olasilikla duzeltmis gorunuyor."
        )
    if llm_preserved and not llm_fixed:
        joined = ", ".join(preserved_labels)
        return (
            f"LLM refaktorleri ({joined}) hatayi buyuk olasilikla tasimaya devam etmis."
        )
    fixed_part = ", ".join(fixed_labels)
    preserved_part = ", ".join(preserved_labels)
    return (
        f"Hatayi duzeltmis gorunen LLM'ler: {fixed_part}. "
        f"Hata tasiyor olabilecek LLM'ler: {preserved_part}."
    )


def _choice_status_labels(lang: str) -> dict[str, str]:
    if lang == "en":
        return {
            "fixed": "Error likely fixed",
            "buggy": "Error likely present",
            "clean": "No hidden error",
            "na": "—",
        }
    return {
        "fixed": "Hata giderildi",
        "buggy": "Hata tasiyor",
        "clean": "Gizli hata yok",
        "na": "—",
    }


def _llm_cell_labels(lang: str) -> dict[str, str]:
    if lang == "en":
        return {"fixed": "Fixed", "preserved": "Still buggy", "na": "—"}
    return {"fixed": "Duzeltti", "preserved": "Hata var", "na": "—"}


def _build_debrief_table(lang: str, questions: list[dict]) -> dict:
    lang = normalize_lang(lang)
    status_labels = _choice_status_labels(lang)
    llm_labels = _llm_cell_labels(lang)
    providers = ("chatgpt", "groq", "gemini", "claude")

    if lang == "en":
        headers = {
            "question": "Q",
            "task": "Task",
            "hidden_bug": "Hidden bug?",
            "your_choice": "Your choice",
            "choice_status": "Your selection",
        }
    else:
        headers = {
            "question": "Soru",
            "task": "Gorev",
            "hidden_bug": "Gizli hata?",
            "your_choice": "Seciminiz",
            "choice_status": "Seciminizde",
        }

    provider_headers = {p: _provider_label(lang, p) for p in providers}
    rows = []

    for q in questions:
        if q.get("has_injected_bug"):
            hidden_bug = "Yes" if lang == "en" else "Evet"
            if q.get("user_fixed") is True:
                choice_status = status_labels["fixed"]
                choice_status_key = "fixed"
            elif q.get("user_fixed") is False:
                choice_status = status_labels["buggy"]
                choice_status_key = "buggy"
            else:
                choice_status = status_labels["na"]
                choice_status_key = "na"
        else:
            hidden_bug = "No" if lang == "en" else "Hayir"
            choice_status = status_labels["clean"]
            choice_status_key = "clean"

        llm_cells = []
        for provider in providers:
            fix_state = (q.get("llm_fix") or {}).get(provider, "na")
            llm_cells.append({
                "provider": provider,
                "label": provider_headers[provider],
                "status": fix_state,
                "text": llm_labels.get(fix_state, llm_labels["na"]),
                "selected": q.get("chosen_source") == provider,
            })

        rows.append({
            "question_number": q.get("question_number"),
            "description": q.get("description") or "",
            "hidden_bug": hidden_bug,
            "choice_label": q.get("choice_label") or "",
            "choice_status": choice_status,
            "choice_status_key": choice_status_key,
            "llm_cells": llm_cells,
            "has_injected_bug": bool(q.get("has_injected_bug")),
        })

    return {
        "headers": headers,
        "provider_headers": provider_headers,
        "rows": rows,
        "providers": list(providers),
    }


def _build_debrief_chart(lang: str, questions: list[dict]) -> dict | None:
    buggy = [q for q in questions if q.get("has_injected_bug")]
    if not buggy:
        return None

    providers = ("chatgpt", "groq", "gemini", "claude")
    colors = {
        "chatgpt": "#10a37f",
        "groq": "#f97316",
        "gemini": "#4285f4",
        "claude": "#d97757",
    }
    labels = [
        (f"Q{q['question_number']}" if lang == "en" else f"Soru {q['question_number']}")
        for q in buggy
    ]
    datasets = []
    for provider in providers:
        datasets.append({
            "provider": provider,
            "label": _provider_label(lang, provider),
            "color": colors[provider],
            "data": [
                1 if (q.get("llm_fix") or {}).get(provider) == "fixed" else 0
                for q in buggy
            ],
        })

    if lang == "en":
        title = "Which LLM likely fixed the hidden bug?"
        y_label = "Fixed (1) / Not fixed (0)"
        legend_fixed = "1 = likely fixed"
        legend_bug = "0 = likely still buggy"
    else:
        title = "Hangi LLM gizli hatayi duzeltmis olabilir?"
        y_label = "Duzeltti (1) / Duzeltmedi (0)"
        legend_fixed = "1 = buyuk olasilikla duzeltti"
        legend_bug = "0 = buyuk olasilikla hata tasiyor"

    return {
        "title": title,
        "y_label": y_label,
        "legend_fixed": legend_fixed,
        "legend_bug": legend_bug,
        "labels": labels,
        "datasets": datasets,
    }


def debrief_strings(lang: str, summary: dict) -> dict:
    """Personal post-survey debrief for the participant's 5 questions."""
    lang = normalize_lang(lang)
    empty = {
        "show": False,
        "title": "",
        "intro": "",
        "footer": "",
        "items": [],
        "table": None,
        "chart": None,
    }
    if not summary.get("show_debrief"):
        return empty

    total = summary["total_questions"]
    buggy_n = summary["buggy_question_count"]
    picked_n = summary["user_picked_buggy_count"]
    all_questions = summary.get("all_questions") or summary.get("buggy_questions") or []

    table = _build_debrief_table(lang, all_questions)
    chart = _build_debrief_chart(lang, all_questions)

    if lang == "en":
        title = "Your session summary"
        if buggy_n == 0:
            intro = (
                f"Among the {total} questions you answered, none contained a "
                "hidden logic error."
            )
            footer = ""
        else:
            intro = (
                f"Among the {total} questions, {buggy_n} contained a hidden logic error. "
                "The table shows whether your choice and each LLM refactor likely fixed it."
            )
            if picked_n > 0:
                footer = (
                    f"In {picked_n} of these {buggy_n} buggy question(s) you selected a version "
                    "that likely still had the error. Always verify code with tests."
                )
            else:
                footer = (
                    "You avoided versions that likely still had the error — "
                    "still verify with tests; looks can be misleading."
                )
    else:
        title = "Oturum ozetiniz"
        if buggy_n == 0:
            intro = f"Cevapladiginiz {total} sorunun hicbirinde gizli mantik hatasi yoktu."
            footer = ""
        else:
            intro = (
                f"Cevapladiginiz {total} sorudan {buggy_n} tanesinde gizli mantik hatasi vardi. "
                "Tablo, seciminizin ve her LLM refaktorunun hatayi gidermis olup olmadigini gosterir."
            )
            if picked_n > 0:
                footer = (
                    f"Bu {buggy_n} sorudan {picked_n} tanesinde hatayi tasiyan versiyonu sectiniz. "
                    "Kodu mutlaka test veya dikkatli inceleme ile dogrulayin."
                )
            else:
                footer = (
                    "Hata tasiyan versiyonu secmediniz. Yine de kodu test etmeden "
                    "yalnizca gorunume guvenmeyin."
                )

    return {
        "show": True,
        "title": title,
        "intro": intro,
        "footer": footer,
        "items": [],
        "table": table,
        "chart": chart,
    }


def study_steps(lang: str) -> list[tuple[str, str]]:
    if lang == "en":
        return [
            ("1. Code review", "You will see 5 different Java code snippets and their tasks, one at a time."),
            ("2. Comparison", "For each snippet, compare the source with four AI versions (ChatGPT, Groq, Google Gemini, Claude)."),
            ("3. Selection", "Choose the version you find most trustworthy in each question."),
        ]
    return [
        ("1. Kod inceleme", "Size 5 farkli Java kodu ve gorevi sirayla aciklanir."),
        ("2. Karsilastirma", "Her kod icin kaynak hali ile dort yapay zeka versiyonunu (ChatGPT, Groq, Google Gemini, Claude) gorursunuz."),
        ("3. Secim", "Her soruda en guvenilir buldugunuz versiyonu secersiniz."),
    ]


def study_notes(lang: str) -> list[str]:
    if lang == "en":
        return [
            "No name, email, or personal information is requested.",
            "Only your version choice is recorded anonymously.",
            "There are no right or wrong answers; your general impression is enough.",
        ]
    return [
        "Ad, e-posta veya kimlik bilgisi istenmez.",
        "Yalnizca hangi versiyonu sectiginiz anonim olarak kaydedilir.",
        "Dogru veya yanlis cevap yoktur; genel izleniminiz yeterlidir.",
    ]


def privacy_footer(lang: str) -> str:
    if lang == "en":
        return (
            "This survey is fully anonymous. No personal information is collected, "
            "and your individual responses are never disclosed."
        )
    return (
        "Bu anket tamamen anonimdir. Kisisel bilginiz toplanmaz ve bireysel "
        "yanitlariniz hicbir yerde aciklanmaz."
    )


def submit_label(index: int, total: int, lang: str) -> str:
    if index >= total - 1:
        return "Complete survey" if lang == "en" else "Anketi tamamla"
    return "Next question" if lang == "en" else "Sonraki soru"


def wake_script(lang: str) -> str:
    if lang == "en":
        title = "Survey server is waking up"
        body = "First load may take 30–60 seconds; please wait."
        retry = "Retrying..."
    else:
        title = "Anket sunucusu uyaniyor"
        body = "Ilk acilis 30-60 sn surebilir; lutfen bekleyin."
        retry = "Yeniden deneniyor..."
    return f"""
<script>
(function () {{
  async function isOperational() {{
    try {{
      var res = await fetch("/health", {{ cache: "no-store" }});
      if (!res.ok) return false;
      var data = await res.json();
      return !!data.operational;
    }} catch (e) {{
      return false;
    }}
  }}
  async function waitForService() {{
    if (await isOperational()) return;
    var banner = document.createElement("div");
    banner.id = "wake-banner";
    banner.style.cssText = "display:flex;position:fixed;inset:0;background:rgba(11,18,32,0.94);z-index:9999;align-items:center;justify-content:center;padding:2rem;text-align:center;color:#eef2ff;font-family:system-ui,sans-serif";
    banner.innerHTML = "<div><h2 style=\\"margin:0 0 1rem\\">{title}</h2><p style=\\"color:#94a3b8;max-width:440px;line-height:1.5\\">{body}</p><p id=\\"wake-status\\" style=\\"margin-top:1rem;color:#22d3ee\\">{retry}</p></div>";
    document.body.appendChild(banner);
    for (var i = 0; i < 18; i++) {{
      if (await isOperational()) {{
        banner.remove();
        return;
      }}
      var status = document.getElementById("wake-status");
      if (status) status.textContent = "{retry} (" + (i + 1) + "/18)";
      await new Promise(function (r) {{ setTimeout(r, 5000); }});
    }}
    location.reload();
  }}
  waitForService();
}})();
</script>
"""


def ui_strings(lang: str) -> dict[str, str]:
    lang = normalize_lang(lang)
    if lang == "en":
        return {
            "html_lang": "en",
            "home_title": "HUMAN-AI Survey",
            "survey_title": "Code Selection · HUMAN-AI",
            "thanks_title": "Thank You · HUMAN-AI",
            "stats_title": "HUMAN-AI Statistics",
            "privacy_banner": "Anonymous survey · No personal info · 5 questions · ~10 minutes",
            "privacy_banner_short": "Anonymous survey · No personal info",
            "subtitle": "Trust research on Java code refactored by AI",
            "lead": (
                "In this survey you will see <strong>5 different Java code snippets</strong>. "
                "For each one, compare the <strong>source version</strong> with "
                "<strong>ChatGPT</strong>, <strong>Groq</strong>, <strong>Google Gemini</strong>, and "
                "<strong>Claude</strong> versions and select the one you find most trustworthy."
            ),
            "how_it_works": "How it works",
            "already_completed": (
                "You have already completed this survey. Each participant may respond only once; "
                "repeat participation is not allowed."
            ),
            "storage_not_ready": (
                "Server or database is waking up. Please wait 30–60 seconds; "
                "the page will refresh automatically."
            ),
            "survey_not_ready": "The survey is not ready right now. Please try again later.",
            "start_survey": "Start survey",
            "view_results": "View results",
            "cta_note": "{n}-question anonymous survey · Each participant may respond once.",
            "step_info": "1. Info",
            "step_code": "2. Code selection",
            "step_done": "3. Complete",
            "question_word": "Question",
            "choose_version": "Select the most trustworthy code version",
            "option_count_hint": "5 versions: Source Code, Google Gemini, ChatGPT, Groq, and Claude — scroll if needed.",
            "click_to_select": "Click to select",
            "thanks_heading": "Thank you",
            "thanks_saved": "All your responses have been saved successfully.",
            "thanks_body": (
                "You completed all {n} questions. Thank you for your contribution. "
                "Your choices are fully anonymous; your name or personal information was not recorded. "
                "You cannot participate again from this device."
            ),
            "home_link": "Home",
            "stats_heading": "Survey Results",
            "stats_lead": "Anonymous aggregate statistics on which code participants trusted more.",
            "stats_anon_note": (
                "All data on this page is anonymous. Individual participant identity, "
                "session details, or selected code details are not shown — only overall preference distribution."
            ),
            "stats_empty_1": "No survey responses recorded yet.",
            "stats_empty_2": "Charts will appear here after the first participant responds.",
            "stat_total": "Total responses",
            "stat_participants": "Anonymous participants",
            "stat_source": "Trusted source code",
            "stat_llm": "Trusted LLM",
            "stat_winner": "Most selected LLM:",
            "chart_source_vs_llm": "Source Code vs LLM",
            "chart_source_vs_llm_sub": "Who trusted the raw source vs AI?",
            "chart_comparison": "Option Comparison",
            "chart_comparison_sub": "Source Code, Google Gemini, ChatGPT, Groq, and Claude selection counts",
            "chart_source_label": "Source Code",
            "chart_llm_label": "LLM",
            "join_survey": "Take survey",
            "bar_dataset": "Selection count",
            "bar_tooltip": " selections",
            "stats_participant_table_title": "Choices vs participants by option",
            "stats_participant_table_sub": (
                "Total selections across all questions, and how many unique participants "
                "picked each option at least once."
            ),
            "stats_col_option": "Option",
            "stats_col_choices": "Total selections",
            "stats_col_participants": "Participants (≥1 pick)",
            "lang_tr": "Turkce",
            "lang_en": "English",
            "lang_switch": "Language",
        }
    return {
        "html_lang": "tr",
        "home_title": "HUMAN-AI Anketi",
        "survey_title": "Kod Secimi · HUMAN-AI",
        "thanks_title": "Tesekkurler · HUMAN-AI",
        "stats_title": "HUMAN-AI Istatistik",
        "privacy_banner": "Anonim anket · Kisisel bilgi istenmez · 5 soru · Yaklasik 10 dakika",
        "privacy_banner_short": "Anonim anket · Kisisel bilgi istenmez",
        "subtitle": "Yapay zeka ile duzenlenmis Java kodlarina guven arastirmasi",
        "lead": (
            "Bu ankette size <strong>5 farkli Java kodu</strong> gosterilir. Her kod icin "
            "<strong>kaynak hali</strong> ile <strong>ChatGPT</strong>, <strong>Groq</strong>, "
            "<strong>Google Gemini</strong> ve <strong>Claude</strong> versiyonlarini karsilastirip en guvenilir buldugunuzu "
            "secmeniz istenir."
        ),
        "how_it_works": "Nasil calisir?",
        "already_completed": (
            "Bu ankete zaten katildiniz. Her katilimci yalnizca bir kez yanit verebilir; "
            "tekrar katilim mumkun degildir."
        ),
        "storage_not_ready": (
            "Sunucu veya veritabani uyaniyor. Lutfen 30-60 saniye bekleyin; "
            "sayfa otomatik yenilenecek."
        ),
        "survey_not_ready": "Anket su an hazir degil. Lutfen daha sonra tekrar deneyin.",
        "start_survey": "Ankete basla",
        "view_results": "Sonuclari gor",
        "cta_note": "{n} soruluk anonim anket · Her katilimci bir kez yanit verebilir.",
        "step_info": "1. Bilgi",
        "step_code": "2. Kod secimi",
        "step_done": "3. Tamamlandi",
        "question_word": "Soru",
        "choose_version": "En guvenilir kod versiyonunu secin",
        "option_count_hint": "5 versiyon: Kaynak Kod, Google Gemini, ChatGPT, Groq ve Claude — gerekirse asagi kaydirin.",
        "click_to_select": "Secmek icin tikla",
        "thanks_heading": "Tesekkurler",
        "thanks_saved": "Tum yanitlariniz basariyla kaydedildi.",
        "thanks_body": (
            "{n} sorunun tamamini tamamladiniz. Katkiniz icin tesekkur ederiz. "
            "Secimleriniz tamamen anonimdir; adiniz veya kisisel bilginiz kaydedilmedi. "
            "Bu cihazdan tekrar katilim mumkun degildir."
        ),
        "home_link": "Ana sayfa",
        "stats_heading": "Anket Sonuclari",
        "stats_lead": "Katilimcilarin hangi koda daha cok guvendigine dair anonim toplu istatistikler.",
        "stats_anon_note": (
            "Bu sayfadaki tum veriler anonimdir. Bireysel katilimci kimligi, oturum bilgisi veya "
            "secilen kod detayi gosterilmez — yalnizca genel tercih dagilimi paylasilir."
        ),
        "stats_empty_1": "Henuz kayitli anket cevabi yok.",
        "stats_empty_2": "Ilk katilimci cevap verdikten sonra grafikler burada gorunecek.",
        "stat_total": "Toplam yanit",
        "stat_participants": "Anonim katilim",
        "stat_source": "Kaynak koda guvenen",
        "stat_llm": "LLM'e guvenen",
        "stat_winner": "En cok tercih edilen LLM:",
        "chart_source_vs_llm": "Kaynak Kod vs LLM",
        "chart_source_vs_llm_sub": "Kim ham kaynak koda, kim yapay zekaya guvenmis?",
        "chart_comparison": "Secenek Karsilastirmasi",
        "chart_comparison_sub": "Kaynak Kod, Google Gemini, ChatGPT, Groq ve Claude tercih sayilari",
        "chart_source_label": "Kaynak Kod",
        "chart_llm_label": "LLM",
        "join_survey": "Ankete katil",
        "bar_dataset": "Secim sayisi",
        "bar_tooltip": " secim",
        "stats_participant_table_title": "Secenek bazinda secim ve katilimci",
        "stats_participant_table_sub": (
            "Tum sorulardaki toplam secimler ve her secenegi en az bir kez "
            "isaretleyen benzersiz katilimci sayisi."
        ),
        "stats_col_option": "Secenek",
        "stats_col_choices": "Toplam secim",
        "stats_col_participants": "Katilimci (en az 1)",
        "lang_tr": "Turkce",
        "lang_en": "English",
        "lang_switch": "Dil",
    }
