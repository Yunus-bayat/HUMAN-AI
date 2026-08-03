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

SOURCE_LABELS = {
    "tr": {
        "original": "Kaynak Kod",
        "gemini": "Gemini",
        "chatgpt": "ChatGPT",
        "groq": "Groq",
        "claude": "Claude",
    },
    "en": {
        "original": "Source Code",
        "gemini": "Gemini",
        "chatgpt": "ChatGPT",
        "groq": "Groq",
        "claude": "Claude",
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
            f"LLM-edited versions (ChatGPT, Groq, Gemini, Claude). "
            f"Please select the one you find most trustworthy."
        )
    return (
        f"Asagida LLM'ler (ChatGPT, Groq, Gemini, Claude) tarafindan duzenlenen "
        f"{topic} kodunun bes versiyonu yer almaktadir. "
        f"Lutfen size en guvenilir geleni seciniz."
    )


def debrief_strings(lang: str, summary: dict) -> dict:
    """Personal post-survey debrief for the participant's 5 questions."""
    lang = normalize_lang(lang)
    if not summary.get("show_debrief"):
        return {"show": False, "title": "", "intro": "", "items": [], "footer": ""}

    total = summary["total_questions"]
    buggy_n = summary["buggy_question_count"]
    picked_n = summary["user_picked_buggy_count"]
    questions = summary.get("buggy_questions") or []

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
                f"Among the {total} questions you answered, {buggy_n} contained a "
                "hidden logic error:"
            )
            items = []
            for q in questions:
                num = q["question_number"]
                desc = q["description"]
                label = q["choice_label"]
                if q["user_picked_buggy"]:
                    items.append(
                        f"Question {num} ({desc}): you selected {label} — "
                        "this version likely still had the error."
                    )
                else:
                    items.append(
                        f"Question {num} ({desc}): you selected {label} — "
                        "this version likely did not carry the error."
                    )
            if picked_n > 0:
                footer = (
                    f"You chose a version that likely still had the error in "
                    f"{picked_n} of these {buggy_n} question(s). "
                    "Blind trust in AI-generated or unreviewed code can hide subtle bugs — "
                    "always verify with tests or careful review."
                )
            else:
                footer = (
                    "You did not select a version that likely still had the error. "
                    "Still, always verify code with tests — looks can be misleading."
                )
            return {"show": True, "title": title, "intro": intro, "items": items, "footer": footer}

        return {"show": True, "title": title, "intro": intro, "items": [], "footer": footer}

    title = "Oturum ozetiniz"
    if buggy_n == 0:
        intro = f"Cevapladiginiz {total} sorunun hicbirinde gizli mantik hatasi yoktu."
        footer = ""
    else:
        intro = f"Cevapladiginiz {total} sorudan {buggy_n} tanesinde gizli mantik hatasi vardi:"
        items = []
        for q in questions:
            num = q["question_number"]
            desc = q["description"]
            label = q["choice_label"]
            if q["user_picked_buggy"]:
                items.append(
                    f"Soru {num} ({desc}): {label} sectiniz — "
                    "bu versiyonda hata buyuk olasilikla korunmustu."
                )
            else:
                items.append(
                    f"Soru {num} ({desc}): {label} sectiniz — "
                    "bu versiyonda hata buyuk olasilikla tasimiyordu."
                )
        if picked_n > 0:
            footer = (
                f"Bu {buggy_n} sorudan {picked_n} tanesinde hatayi tasiyan versiyonu sectiniz. "
                "Yapay zekaya veya incelenmemis koda körü körüne güvenmek tam da bu riski dogurur — "
                "kodu mutlaka test veya dikkatli inceleme ile dogrulayin."
            )
        else:
            footer = (
                "Hata tasiyan versiyonu secmediniz. Yine de kodu test etmeden "
                "yalnizca gorunume guvenmeyin."
            )
        return {"show": True, "title": title, "intro": intro, "items": items, "footer": footer}

    return {"show": True, "title": title, "intro": intro, "items": [], "footer": footer}


def study_steps(lang: str) -> list[tuple[str, str]]:
    if lang == "en":
        return [
            ("1. Code review", "You will see 5 different Java code snippets and their tasks, one at a time."),
            ("2. Comparison", "For each snippet, compare the source with four AI versions (ChatGPT, Groq, Gemini, Claude)."),
            ("3. Selection", "Choose the version you find most trustworthy in each question."),
        ]
    return [
        ("1. Kod inceleme", "Size 5 farkli Java kodu ve gorevi sirayla aciklanir."),
        ("2. Karsilastirma", "Her kod icin kaynak hali ile dort yapay zeka versiyonunu (ChatGPT, Groq, Gemini, Claude) gorursunuz."),
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
                "<strong>ChatGPT</strong>, <strong>Groq</strong>, <strong>Gemini</strong>, and "
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
            "option_count_hint": "5 versions: Source Code, Gemini, ChatGPT, Groq, and Claude — scroll if needed.",
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
            "chart_comparison_sub": "Source Code, Gemini, ChatGPT, Groq, and Claude selection counts",
            "chart_source_label": "Source Code",
            "chart_llm_label": "LLM",
            "join_survey": "Take survey",
            "bar_dataset": "Selection count",
            "bar_tooltip": " selections",
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
            "<strong>Gemini</strong> ve <strong>Claude</strong> versiyonlarini karsilastirip en guvenilir buldugunuzu "
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
        "option_count_hint": "5 versiyon: Kaynak Kod, Gemini, ChatGPT, Groq ve Claude — gerekirse asagi kaydirin.",
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
        "chart_comparison_sub": "Kaynak Kod, Gemini, ChatGPT, Groq ve Claude tercih sayilari",
        "chart_source_label": "Kaynak Kod",
        "chart_llm_label": "LLM",
        "join_survey": "Ankete katil",
        "bar_dataset": "Secim sayisi",
        "bar_tooltip": " secim",
        "lang_tr": "Turkce",
        "lang_en": "English",
        "lang_switch": "Dil",
    }
