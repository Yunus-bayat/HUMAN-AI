"""Blind code-choice survey for measuring trust in LLM refactors."""

from __future__ import annotations

import json
import os
import random
import sys
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, g, make_response, redirect, render_template_string, request, session, url_for

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "app"))
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from analyze_results import analyze, load_rows  # noqa: E402
from results_store import (  # noqa: E402
    CompletedParticipantStore,
    SurveySessionStore,
    append_result,
    ensure_schema,
    fetch_choices_for_response,
    storage_backend,
    storage_health,
    storage_operational,
)
from bug_presence import choice_still_has_bug, summarize_session_debrief  # noqa: E402

_STORAGE_CHECK_CACHE: dict[str, float | bool] = {"at": 0.0, "ok": False}
_STORAGE_CHECK_TTL = 30.0


def cached_storage_operational() -> bool:
    import time

    now = time.time()
    if now - float(_STORAGE_CHECK_CACHE["at"]) < _STORAGE_CHECK_TTL:
        return bool(_STORAGE_CHECK_CACHE["ok"])
    ok = storage_operational()
    _STORAGE_CHECK_CACHE["at"] = now
    _STORAGE_CHECK_CACHE["ok"] = ok
    return ok
from code_categories import (  # noqa: E402
    CATEGORIES,
    build_four_way_survey_prompt,
    category_for,
)
from survey_i18n import (  # noqa: E402
    CATEGORY_TOPICS_EN,
    DEFAULT_LANG,
    SOURCE_LABELS,
    build_survey_prompt,
    debrief_strings,
    localized_category_label,
    localized_description,
    normalize_lang,
    privacy_footer,
    study_notes,
    study_steps,
    submit_label,
    ui_strings,
    wake_script,
)

REFACTORED_PATH = os.path.join(ROOT, "data", "refactored", "refactored_dataset.json")
SESSIONS_PATH = os.path.join(ROOT, "data", "results", "active_sessions.json")
COMPLETED_TOKENS_PATH = os.path.join(ROOT, "data", "results", "completed_tokens.json")
COMPLETED_COOKIE = "ha_survey_completed"
COMPLETED_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

PREFERRED_SOURCES = ("original", "chatgpt", "groq", "gemini", "claude")
OPTION_ORDER = ("original", "gemini", "chatgpt", "groq", "claude")
SURVEY_MODE = "five_way"
LLM_REFACTOR_NAMES = ("chatgpt", "groq", "gemini", "claude")
QUESTIONS_PER_SESSION = 5

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "human-ai-dev-secret")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

try:
    ensure_schema()
    health = storage_health()
    print(
        f"[HUMAN-AI] Depolama: {health['backend']} | "
        f"Kalici: {health['persistent']} | "
        f"Baglanti: {'OK' if health['database_connected'] else 'HATA'} | "
        f"Kayit: {health['choices_count']} cevap, {health['participant_count']} katilimci",
        flush=True,
    )
    if not health["operational"]:
        print(f"[HUMAN-AI] UYARI: {health['database_error']}", flush=True)
except Exception as exc:
    print(f"[HUMAN-AI] Depolama baslatilamadi ({storage_backend()}): {exc}", flush=True)


@app.before_request
def _resolve_lang():
    query_lang = request.args.get("lang")
    if query_lang:
        g.lang = normalize_lang(query_lang)
        session["lang"] = g.lang
        session.modified = True
    else:
        g.lang = normalize_lang(session.get("lang"))


def current_lang() -> str:
    return getattr(g, "lang", DEFAULT_LANG)


def source_labels_for(lang: str | None = None) -> dict[str, str]:
    lang = normalize_lang(lang or current_lang())
    return SOURCE_LABELS[lang]


BASE_CSS = """
:root {
  --bg0: #0b1220;
  --bg1: #121a2b;
  --card: rgba(255, 255, 255, 0.04);
  --card-hover: rgba(255, 255, 255, 0.07);
  --ink: #eef2ff;
  --muted: #94a3b8;
  --line: rgba(148, 163, 184, 0.18);
  --accent: #22d3ee;
  --accent2: #818cf8;
  --shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
  --source: #64748b;
  --gemini: #4285f4;
  --chatgpt: #10a37f;
  --groq: #f97316;
  --claude: #d97757;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  font-family: "DM Sans", "Segoe UI", sans-serif;
  color: var(--ink);
  background:
    radial-gradient(900px 500px at 10% -10%, rgba(34, 211, 238, 0.18), transparent 60%),
    radial-gradient(700px 420px at 100% 0%, rgba(129, 140, 248, 0.16), transparent 55%),
    linear-gradient(165deg, var(--bg0), var(--bg1));
}
.wrap { width: min(1180px, calc(100% - 2rem)); margin: 0 auto; padding: 2rem 0 4rem; }
.hero { margin-bottom: 1.5rem; }
.brand {
  font-family: "Space Grotesk", "Segoe UI", sans-serif;
  font-size: clamp(2.2rem, 4vw, 3.4rem);
  letter-spacing: -0.04em;
  margin: 0 0 0.35rem;
  background: linear-gradient(90deg, #fff, #cbd5e1 55%, #22d3ee);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.lead { color: var(--muted); max-width: 46rem; line-height: 1.65; font-size: 1.02rem; }
.lead strong { color: var(--ink); font-weight: 600; }
.code-brief {
  margin: 1rem 0 0.5rem;
  padding: 1rem 1.15rem;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.03);
}
.code-brief-label {
  display: inline-block;
  margin-bottom: 0.35rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
}
.code-brief-title {
  margin: 0;
  font-family: "Space Grotesk", "Segoe UI", sans-serif;
  font-size: clamp(1.15rem, 2vw, 1.45rem);
  line-height: 1.35;
  color: var(--ink);
}
.panel h2 { margin: 0 0 1rem; font-family: "Space Grotesk", "Segoe UI", sans-serif; font-size: 1.1rem; }
.panel {
  margin-top: 1.25rem;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: var(--shadow);
  padding: 1.35rem 1.5rem;
  backdrop-filter: blur(12px);
}
.chips { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.75rem 0 0; }
.chip {
  font-size: 0.78rem;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--muted);
}
.chip.ok { color: #a7f3d0; border-color: rgba(167, 243, 208, 0.35); }
.chip.warn { color: #fde68a; border-color: rgba(253, 230, 138, 0.35); }
.meta { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid var(--line);
  color: var(--ink);
  background: rgba(255,255,255,0.03);
}
h2 {
  font-family: "Space Grotesk", sans-serif;
  margin: 0.2rem 0 0.9rem;
  font-size: 1.35rem;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}
@media (max-width: 1100px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
.option-card {
  position: relative;
  border: 2px solid var(--line);
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.55);
  overflow: hidden;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}
.option-card:hover { transform: translateY(-2px); border-color: rgba(34, 211, 238, 0.35); }
.option-card:has(input:checked) {
  border-color: var(--accent);
  box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.25), 0 16px 40px rgba(34, 211, 238, 0.12);
}
.option-card input { position: absolute; opacity: 0; pointer-events: none; }
.option-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--line);
  cursor: pointer;
}
.badge {
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  color: #fff;
}
.badge.source { background: var(--source); }
.badge.gemini { background: var(--gemini); }
.badge.chatgpt { background: var(--chatgpt); }
.badge.groq { background: var(--groq); }
.badge.claude { background: var(--claude); }
.pick-hint { font-size: 0.75rem; color: var(--muted); }
pre {
  margin: 0;
  overflow: auto;
  max-height: 300px;
  padding: 1rem;
  background: #0a0f18;
  color: #dbeafe;
  font-family: "JetBrains Mono", "Cascadia Code", Consolas, monospace;
  font-size: 0.76rem;
  line-height: 1.5;
}
.actions { margin-top: 1.35rem; display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center; }
button, .btn {
  appearance: none;
  border: 0;
  background: linear-gradient(135deg, #22d3ee, #818cf8);
  color: #041016;
  padding: 0.85rem 1.35rem;
  font: inherit;
  font-weight: 700;
  border-radius: 12px;
  cursor: pointer;
  text-decoration: none;
  box-shadow: 0 10px 30px rgba(34, 211, 238, 0.25);
}
button:hover, .btn:hover { filter: brightness(1.05); }
button.secondary, .btn.secondary {
  background: transparent;
  color: var(--ink);
  border: 1px solid var(--line);
  box-shadow: none;
}
.notice { margin-top: 1rem; color: #fca5a5; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0;
}
.stat-box {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 0.9rem 1rem;
}
.stat-box strong { display: block; font-size: 1.4rem; margin-top: 0.25rem; }
ul.clean { margin: 0.4rem 0 0; padding-left: 1.1rem; color: var(--muted); }
.anon-note {
  margin: 0 0 1.25rem;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(34, 211, 238, 0.25);
  background: rgba(34, 211, 238, 0.08);
  color: #bae6fd;
  font-size: 0.92rem;
  line-height: 1.55;
}
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.25rem;
  margin: 1.5rem 0;
}
.chart-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 1.15rem 1.15rem 1.35rem;
}
.chart-card h2 {
  margin: 0 0 0.25rem;
  font-family: "Space Grotesk", "Segoe UI", sans-serif;
  font-size: 1.15rem;
}
.chart-sub { margin: 0 0 1rem; color: var(--muted); font-size: 0.88rem; }
.chart-wrap { position: relative; height: 280px; }
.legend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 1rem;
  margin-top: 1rem;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--muted);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.empty-charts {
  text-align: center;
  padding: 2.5rem 1rem;
  color: var(--muted);
}
.info-panel { margin-top: 0; }
.info-panel h2 {
  margin: 0 0 0.75rem;
  font-family: "Space Grotesk", "Segoe UI", sans-serif;
  font-size: 1.25rem;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0;
}
.info-step {
  padding: 0.85rem 0.95rem;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
}
.info-step strong {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
}
.info-step span { color: var(--muted); font-size: 0.9rem; line-height: 1.5; }
.info-notes {
  margin: 0.75rem 0 0;
  padding-left: 1.1rem;
  color: var(--muted);
  line-height: 1.6;
  font-size: 0.92rem;
}
.info-notes li + li { margin-top: 0.35rem; }
.debrief-panel {
  margin: 1.25rem 0 0;
  padding: 1rem 1.15rem;
  border-radius: 14px;
  border: 1px solid rgba(251, 191, 36, 0.35);
  background: rgba(251, 191, 36, 0.08);
  color: #fde68a;
  line-height: 1.65;
  font-size: 0.92rem;
}
.debrief-panel h3 {
  margin: 0 0 0.5rem;
  font-family: "Space Grotesk", "Segoe UI", sans-serif;
  font-size: 1.05rem;
  color: #fef3c7;
}
.debrief-panel p { margin: 0 0 0.65rem; }
.debrief-panel p:last-child { margin-bottom: 0; }
.debrief-list {
  margin: 0.5rem 0 0.75rem;
  padding-left: 1.1rem;
  color: #fef9c3;
}
.debrief-list li { margin-bottom: 0.45rem; line-height: 1.55; }
.debrief-list li:last-child { margin-bottom: 0; }
.study-info {
  margin-bottom: 1rem;
  border: 1px solid rgba(34, 211, 238, 0.2);
  border-radius: 14px;
  background: rgba(34, 211, 238, 0.06);
  overflow: hidden;
}
.study-info summary {
  cursor: pointer;
  padding: 0.85rem 1rem;
  font-weight: 600;
  color: #bae6fd;
  list-style: none;
}
.study-info summary::-webkit-details-marker { display: none; }
.study-info summary::after {
  content: "+";
  float: right;
  color: var(--accent);
  font-weight: 700;
}
.study-info[open] summary::after { content: "−"; }
.study-info-body {
  padding: 0 1rem 1rem;
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.6;
}
.study-info-body p { margin: 0 0 0.65rem; }
.privacy-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  padding: 0.65rem 0.9rem;
  border-radius: 12px;
  border: 1px solid rgba(34, 211, 238, 0.28);
  background: rgba(34, 211, 238, 0.08);
  color: #bae6fd;
  font-size: 0.88rem;
  font-weight: 500;
}
.privacy-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34d399;
  flex-shrink: 0;
}
.subtitle {
  margin: 0 0 0.75rem;
  color: var(--muted);
  font-size: 1.05rem;
}
.steps-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 1.25rem 0;
}
@media (max-width: 760px) { .steps-row { grid-template-columns: 1fr; } }
.step-card {
  padding: 1rem;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.02);
}
.step-num {
  display: inline-block;
  margin-bottom: 0.45rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent2);
}
.step-card p { margin: 0; color: var(--muted); font-size: 0.9rem; line-height: 1.55; }
.cta-note { margin: 0.75rem 0 0; color: var(--muted); font-size: 0.88rem; }
.page-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.55;
}
.survey-steps {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.survey-step {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  color: var(--muted);
}
.survey-step.active {
  color: #041016;
  background: linear-gradient(135deg, #22d3ee, #818cf8);
  border-color: transparent;
}
.survey-step.done {
  color: #a7f3d0;
  border-color: rgba(167, 243, 208, 0.35);
}
.thanks-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  margin-bottom: 0.75rem;
  background: rgba(52, 211, 153, 0.15);
  color: #6ee7b7;
  font-size: 1.4rem;
  font-weight: 700;
}
.progress-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.45rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--ink);
}
.progress-head span:last-child { color: var(--accent); }
.progress-track {
  height: 8px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.15);
  overflow: hidden;
  margin-bottom: 1.25rem;
}
.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #22d3ee, #818cf8);
  transition: width 0.25s ease;
}
.lang-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.82rem;
}
.lang-bar > span { color: var(--muted); }
.lang-bar a {
  color: var(--muted);
  text-decoration: none;
  padding: 0.25rem 0.55rem;
  border-radius: 8px;
  border: 1px solid transparent;
}
.lang-bar a:hover { color: var(--ink); border-color: var(--line); }
.lang-bar a.active {
  color: var(--ink);
  border-color: rgba(34, 211, 238, 0.35);
  background: rgba(34, 211, 238, 0.08);
}
"""

FONT_LINK = (
    "https://fonts.googleapis.com/css2?"
    "family=DM+Sans:wght@400;500;600;700&"
    "family=JetBrains+Mono:wght@400;500&"
    "family=Space+Grotesk:wght@500;600;700&display=swap"
)

LANG_SWITCHER = """
<div class="lang-bar">
  <span>{{ txt.lang_switch }}:</span>
  <a href="{{ url_for('set_lang', lang_code='tr', next=request.full_path) }}" class="{{ 'active' if lang == 'tr' else '' }}">{{ txt.lang_tr }}</a>
  <a href="{{ url_for('set_lang', lang_code='en', next=request.full_path) }}" class="{{ 'active' if lang == 'en' else '' }}">{{ txt.lang_en }}</a>
</div>
"""

HOME_HTML = """
<!doctype html>
<html lang="{{ txt.html_lang }}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ txt.home_title }}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="{{ font_link }}" rel="stylesheet">
  <style>{{ css }}</style>
</head>
<body>
  <main class="wrap">
    {{ lang_switcher | safe }}
    <div class="privacy-banner">
      <span class="privacy-dot"></span>
      {{ txt.privacy_banner }}
    </div>
    <div class="hero">
      <h1 class="brand">HUMAN-AI</h1>
      <p class="subtitle">{{ txt.subtitle }}</p>
      <p class="lead">{{ txt.lead | safe }}</p>
    </div>

    <div class="panel info-panel">
      <h2>{{ txt.how_it_works }}</h2>
      <div class="steps-row">
        {% for title, text in study_steps %}
          <div class="step-card">
            <span class="step-num">{{ title }}</span>
            <p>{{ text }}</p>
          </div>
        {% endfor %}
      </div>
      <ul class="info-notes">
        {% for note in study_notes %}
          <li>{{ note }}</li>
        {% endfor %}
      </ul>
    </div>

    <div class="panel">
      {% if already_completed %}
        <p class="anon-note" style="margin-top:0">{{ txt.already_completed }}</p>
        <div class="actions">
          <a class="btn secondary" href="{{ url_for('stats') }}">{{ txt.view_results }}</a>
        </div>
      {% elif not storage_ready %}
        <p class="notice">{{ txt.storage_not_ready }}</p>
        <meta http-equiv="refresh" content="8" />
      {% elif full_ready_count < questions_per_session %}
        <p class="notice">{{ txt.survey_not_ready }}</p>
      {% else %}
        <form method="post" action="{{ url_for('start') }}" class="actions">
          <button type="submit">{{ txt.start_survey }}</button>
          <a class="btn secondary" href="{{ url_for('stats') }}">{{ txt.view_results }}</a>
        </form>
        <p class="cta-note">{{ cta_note }}</p>
      {% endif %}
    </div>

    <footer class="page-footer">{{ privacy_footer_text }}</footer>
  </main>
  {{ wake_script | safe }}
</body>
</html>
"""

SURVEY_HTML = """
<!doctype html>
<html lang="{{ txt.html_lang }}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ txt.survey_title }}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="{{ font_link }}" rel="stylesheet">
  <style>{{ css }}</style>
</head>
<body>
  <main class="wrap">
    {{ lang_switcher | safe }}
    <div class="privacy-banner">
      <span class="privacy-dot"></span>
      {{ txt.privacy_banner_short }}
    </div>
    <div class="survey-steps">
      <span class="survey-step done">{{ txt.step_info }}</span>
      <span class="survey-step active">{{ txt.step_code }}</span>
      <span class="survey-step">{{ txt.step_done }}</span>
    </div>
    <div class="progress-head">
      <span>{{ txt.question_word }} {{ question_number }} / {{ total_questions }}</span>
      <span>{{ progress_pct }}%</span>
    </div>
    <div class="progress-track">
      <div class="progress-fill" style="width: {{ progress_pct }}%"></div>
    </div>
    <div class="hero">
      <h1 class="brand">HUMAN-AI</h1>
      <div class="code-brief">
        <span class="code-brief-label">{{ current.category_label }}</span>
        <h2 class="code-brief-title">{{ current.description }}</h2>
      </div>
      <p class="lead">{{ current.prompt }}</p>
    </div>
    <div class="panel">
      <h2>{{ txt.choose_version }}</h2>
      <p class="cta-note" style="margin-top:0">{{ txt.option_count_hint }}</p>
      <form method="post">
        <input type="hidden" name="response_id" value="{{ response_id }}" />
        <div class="grid">
          {% for option in options %}
          <label class="option-card">
            <input type="radio" name="choice" value="{{ option.key }}" required />
            <div class="option-head">
              <span class="badge {{ option.badge }}">{{ option.label }}</span>
              <span class="pick-hint">{{ txt.click_to_select }}</span>
            </div>
            <pre>{{ option.code }}</pre>
          </label>
          {% endfor %}
        </div>
        <div class="actions">
          <button type="submit">{{ submit_label }}</button>
        </div>
      </form>
    </div>
    <footer class="page-footer">{{ privacy_footer_text }}</footer>
  </main>
  {{ wake_script | safe }}
</body>
</html>
"""

THANKS_HTML = """
<!doctype html>
<html lang="{{ txt.html_lang }}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ txt.thanks_title }}</title>
  <link href="{{ font_link }}" rel="stylesheet">
  <style>{{ css }}</style>
</head>
<body>
  <main class="wrap">
    {{ lang_switcher | safe }}
    <div class="survey-steps">
      <span class="survey-step done">{{ txt.step_info }}</span>
      <span class="survey-step done">{{ txt.step_code }}</span>
      <span class="survey-step active">{{ txt.step_done }}</span>
    </div>
    <div class="hero"><h1 class="brand">{{ txt.thanks_heading }}</h1></div>
    <div class="panel">
      <div class="thanks-icon">&#10003;</div>
      <p class="lead">{{ txt.thanks_saved }}</p>
      <p style="color:var(--muted);margin-top:0.5rem;line-height:1.6">{{ thanks_body }}</p>
      {% if debrief.show %}
      <div class="debrief-panel">
        <h3>{{ debrief.title }}</h3>
        <p>{{ debrief.intro }}</p>
        {% if debrief['items'] %}
        <ul class="debrief-list">
          {% for item in debrief['items'] %}
            <li>{{ item }}</li>
          {% endfor %}
        </ul>
        {% endif %}
        {% if debrief.footer %}
          <p>{{ debrief.footer }}</p>
        {% endif %}
      </div>
      {% endif %}
      <div class="actions">
        <a class="btn secondary" href="{{ url_for('home') }}">{{ txt.home_link }}</a>
      </div>
    </div>
    <footer class="page-footer">{{ privacy_footer_text }}</footer>
  </main>
</body>
</html>
"""

STATS_HTML = """
<!doctype html>
<html lang="{{ txt.html_lang }}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ txt.stats_title }}</title>
  <link href="{{ font_link }}" rel="stylesheet">
  <style>{{ css }}</style>
</head>
<body>
  <main class="wrap">
    {{ lang_switcher | safe }}
    <div class="hero">
      <h1 class="brand">{{ txt.stats_heading }}</h1>
      <p class="lead">{{ txt.stats_lead }}</p>
    </div>
    <div class="panel">
      <p class="anon-note">{{ txt.stats_anon_note }}</p>

      {% if total == 0 %}
        <div class="empty-charts">
          <p>{{ txt.stats_empty_1 }}</p>
          <p>{{ txt.stats_empty_2 }}</p>
        </div>
      {% else %}
        <div class="stats-grid">
          <div class="stat-box"><span>{{ txt.stat_total }}</span><strong>{{ total }}</strong></div>
          <div class="stat-box"><span>{{ txt.stat_participants }}</span><strong>{{ participants }}</strong></div>
          <div class="stat-box"><span>{{ txt.stat_source }}</span><strong>{{ source_count }} ({{ source_pct }}%)</strong></div>
          <div class="stat-box"><span>{{ txt.stat_llm }}</span><strong>{{ llm_count }} ({{ llm_pct }}%)</strong></div>
        </div>

        {% if winner %}
          <p style="margin:0.5rem 0 0;color:var(--ink)">
            <strong>{{ txt.stat_winner }}</strong> {{ winner }}
          </p>
        {% endif %}

        <div class="charts-grid">
          <div class="chart-card">
            <h2>{{ txt.chart_source_vs_llm }}</h2>
            <p class="chart-sub">{{ txt.chart_source_vs_llm_sub }}</p>
            <div class="chart-wrap"><canvas id="pieTrust"></canvas></div>
            <div class="legend-row">
              <span class="legend-item"><span class="legend-dot" style="background:#64748b"></span>{{ txt.chart_source_label }} · {{ source_count }}</span>
              <span class="legend-item"><span class="legend-dot" style="background:#818cf8"></span>{{ txt.chart_llm_label }} · {{ llm_count }}</span>
            </div>
          </div>
          <div class="chart-card">
            <h2>{{ txt.chart_comparison }}</h2>
            <p class="chart-sub">{{ txt.chart_comparison_sub }}</p>
            <div class="chart-wrap"><canvas id="barAll"></canvas></div>
            <div class="legend-row">
              {% for label, count, pct in all_rows %}
                <span class="legend-item">
                  <span class="legend-dot" style="background:{{ chart_colors[loop.index0] }}"></span>
                  {{ label }} · {{ count }} ({{ pct }}%)
                </span>
              {% endfor %}
            </div>
          </div>
        </div>
      {% endif %}

      <div class="actions">
        <a class="btn" href="{{ url_for('home') }}">{{ txt.home_link }}</a>
        <form method="post" action="{{ url_for('start') }}" style="display:inline">
          <button type="submit" class="btn secondary">{{ txt.join_survey }}</button>
        </form>
      </div>
    </div>
  </main>
  {% if total > 0 %}
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <script>
    const chartDefaults = {
      color: "#94a3b8",
      borderColor: "rgba(148, 163, 184, 0.15)",
    };
    Chart.defaults.color = chartDefaults.color;
    Chart.defaults.borderColor = chartDefaults.borderColor;
    Chart.defaults.font.family = "'DM Sans', 'Segoe UI', sans-serif";

    const pieData = {{ pie_data | tojson }};
    new Chart(document.getElementById("pieTrust"), {
      type: "pie",
      data: {
        labels: pieData.labels,
        datasets: [{
          data: pieData.values,
          backgroundColor: pieData.colors,
          borderWidth: 2,
          borderColor: "#121a2b",
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label(ctx) {
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = total ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                return ` ${ctx.label}: ${ctx.raw} (${pct}%)`;
              },
            },
          },
        },
      },
    });

    const barData = {{ bar_data | tojson }};
    const barTooltipSuffix = {{ bar_tooltip_suffix | tojson }};
    new Chart(document.getElementById("barAll"), {
      type: "bar",
      data: {
        labels: barData.labels,
        datasets: [{
          label: {{ bar_dataset_label | tojson }},
          data: barData.values,
          backgroundColor: barData.colors,
          borderRadius: 10,
          borderSkipped: false,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label(ctx) {
                const total = barData.values.reduce((a, b) => a + b, 0);
                const pct = total ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                return ` ${ctx.raw}${barTooltipSuffix} (${pct}%)`;
              },
            },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { weight: "600" } },
          },
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, precision: 0 },
            grid: { color: "rgba(148, 163, 184, 0.12)" },
          },
        },
      },
    });
  </script>
  {% endif %}
</body>
</html>
"""


def source_code(item):
    return item.get("code_for_llm") or item.get("original_code") or ""


def is_full_ready(item) -> bool:
    ref = item.get("refactored", {}) or {}
    if not source_code(item):
        return False
    return all(ref.get(name) for name in LLM_REFACTOR_NAMES)


def load_ready_items():
    if not os.path.exists(REFACTORED_PATH):
        return []
    with open(REFACTORED_PATH, encoding="utf-8") as f:
        items = json.load(f)
    ready = [item for item in items if is_full_ready(item)]
    for item in ready:
        if "category" not in item:
            cid = category_for(item["id"])
            item["category"] = cid
            item["category_label"] = CATEGORIES[cid]["label"]
            item["category_topic"] = CATEGORIES[cid].get("topic", CATEGORIES[cid]["label"].lower())
    return ready


survey_sessions = SurveySessionStore(SESSIONS_PATH)
completed_participants = CompletedParticipantStore(COMPLETED_TOKENS_PATH)


def participant_already_completed() -> bool:
    token = request.cookies.get(COMPLETED_COOKIE)
    return completed_participants.has_token(token)


def mark_participant_completed(response):
    token = request.cookies.get(COMPLETED_COOKIE)
    if not token or not completed_participants.has_token(token):
        token = str(uuid.uuid4())
        completed_participants.register(token)
    response.set_cookie(
        COMPLETED_COOKIE,
        token,
        max_age=COMPLETED_COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
    )
    return response


BADGE_CLASS = {
    "original": "source",
    "gemini": "gemini",
    "chatgpt": "chatgpt",
    "groq": "groq",
    "claude": "claude",
}


def build_four_options(item, lang: str | None = None):
    labels = source_labels_for(lang)
    pool = {
        "original": source_code(item),
        "chatgpt": item["refactored"]["chatgpt"],
        "groq": item["refactored"]["groq"],
        "gemini": item["refactored"]["gemini"],
        "claude": item["refactored"]["claude"],
    }
    options = []
    for key in OPTION_ORDER:
        options.append({
            "key": key,
            "label": labels[key],
            "badge": BADGE_CLASS[key],
            "code": pool[key],
        })
    return options


def question_prompt(item: dict, lang: str) -> str:
    cid = item.get("category") or category_for(item["id"])
    if lang == "en":
        topic = CATEGORY_TOPICS_EN.get(cid, item.get("category_topic", ""))
        return build_survey_prompt(topic, "en")
    return build_four_way_survey_prompt(item)


def build_question_view(item: dict, lang: str | None = None) -> dict:
    lang = normalize_lang(lang or current_lang())
    cid = item.get("category") or category_for(item["id"])
    return {
        "code_id": item["id"],
        "description": localized_description(item, lang),
        "category": cid,
        "category_label": localized_category_label(
            cid, item.get("category_label", ""), lang
        ),
        "category_topic": item.get("category_topic", ""),
        "prompt": question_prompt(item, lang),
        "has_injected_bug": bool(item.get("has_injected_bug")),
        "bug_type": item.get("bug_type"),
        "bug_id": item.get("bug_id"),
        "options": build_four_options(item, lang),
    }


def ready_items_map() -> dict[str, dict]:
    return {item["id"]: item for item in load_ready_items()}


def build_debrief_context(response_id: str | None, lang: str) -> dict:
    answers = fetch_choices_for_response(response_id)
    summary = summarize_session_debrief(answers, ready_items_map())
    return debrief_strings(lang, summary)


def page_context(**extra):
    lang = current_lang()
    txt = ui_strings(lang)
    return {
        "lang": lang,
        "txt": txt,
        "css": BASE_CSS,
        "font_link": FONT_LINK,
        "lang_switcher": render_template_string(LANG_SWITCHER, lang=lang, txt=txt),
        "privacy_footer_text": privacy_footer(lang),
        "wake_script": wake_script(lang),
        **extra,
    }


def get_response_id() -> str | None:
    return (
        request.args.get("response_id")
        or request.form.get("response_id")
        or session.get("response_id")
    )


def load_active_question(state: dict, lang: str | None = None) -> dict | None:
    question_ids = state.get("question_ids") or []
    index = int(state.get("index", 0))
    if index < 0 or index >= len(question_ids):
        return None
    item = ready_items_map().get(question_ids[index])
    if not item:
        return None
    return build_question_view(item, lang)


def progress_for(index: int, total: int = QUESTIONS_PER_SESSION) -> tuple[int, int]:
    number = index + 1
    pct = int((number / total) * 100)
    return number, pct


@app.get("/lang/<lang_code>")
def set_lang(lang_code: str):
    lang = normalize_lang(lang_code)
    session["lang"] = lang
    session.modified = True
    target = request.args.get("next", "")
    if target.startswith("/"):
        return redirect(target)
    return redirect(url_for("home"))


@app.get("/")
def home():
    ready = load_ready_items()
    lang = current_lang()
    txt = ui_strings(lang)
    return render_template_string(
        HOME_HTML,
        **page_context(
            full_ready_count=len(ready),
            questions_per_session=QUESTIONS_PER_SESSION,
            study_steps=study_steps(lang),
            study_notes=study_notes(lang),
            cta_note=txt["cta_note"].format(n=QUESTIONS_PER_SESSION),
            already_completed=participant_already_completed(),
            storage_ready=cached_storage_operational(),
        ),
    )


@app.get("/health")
def health():
    from flask import jsonify

    data = storage_health()
    status = 200 if data["operational"] else 503
    return jsonify(data), status


@app.post("/start")
def start():
    if not cached_storage_operational():
        return redirect(url_for("home"))
    if participant_already_completed():
        return redirect(url_for("home"))

    ready = load_ready_items()
    if len(ready) < QUESTIONS_PER_SESSION:
        return redirect(url_for("home"))

    old_id = session.get("response_id")
    survey_sessions.delete(old_id)

    picked = random.sample(ready, QUESTIONS_PER_SESSION)
    response_id = survey_sessions.create([item["id"] for item in picked])

    saved_lang = session.get("lang")
    session.clear()
    session["response_id"] = response_id
    if saved_lang:
        session["lang"] = saved_lang
    session.modified = True
    return redirect(url_for("survey", response_id=response_id))


@app.route("/survey", methods=["GET", "POST"])
def survey():
    if participant_already_completed():
        return redirect(url_for("home"))

    response_id = get_response_id()
    if response_id:
        if session.get("response_id") != response_id:
            session["response_id"] = response_id
            session.modified = True
        if request.method == "GET" and not request.args.get("response_id"):
            return redirect(url_for("survey", response_id=response_id))

    state = survey_sessions.get(response_id)
    if not state or state.get("completed"):
        return redirect(url_for("home"))

    index = int(state.get("index", 0))
    total = int(state.get("total", QUESTIONS_PER_SESSION))
    lang = current_lang()
    current = load_active_question(state, lang)
    if not current:
        return redirect(url_for("home"))

    valid_choices = set(PREFERRED_SOURCES)

    if request.method == "POST":
        choice = request.form.get("choice")
        if choice not in valid_choices:
            return redirect(url_for("survey", response_id=response_id))

        question_number, _ = progress_for(index, total)
        labels = source_labels_for(lang)
        item = ready_items_map().get(current["code_id"], {})
        chosen_had_bug = choice_still_has_bug(item, choice)
        answer = {
            "response_id": response_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "survey_mode": SURVEY_MODE,
            "session_questions": total,
            "question_number": question_number,
            "code_id": current["code_id"],
            "description": current["description"],
            "category": current.get("category"),
            "category_label": current.get("category_label"),
            "choice_label": labels[choice],
            "chosen_source": choice,
            "chosen_had_bug": chosen_had_bug,
            "has_injected_bug": bool(current.get("has_injected_bug")),
            "bug_type": current.get("bug_type"),
            "bug_id": current.get("bug_id"),
            "ui_lang": lang,
        }
        append_result(answer)

        state = survey_sessions.advance(response_id)
        if not state:
            return redirect(url_for("home"))

        if state.get("completed"):
            session["survey_completed"] = True
            session["total_questions"] = total
            session.modified = True
            return redirect(url_for("thanks"))

        return redirect(url_for("survey", response_id=response_id))

    question_number, progress_pct = progress_for(index, total)
    return render_template_string(
        SURVEY_HTML,
        **page_context(
            current=current,
            options=current["options"],
            question_number=question_number,
            total_questions=total,
            progress_pct=progress_pct,
            submit_label=submit_label(index, total, lang),
            response_id=response_id,
        ),
    )


@app.get("/thanks")
def thanks():
    response_id = session.get("response_id")
    state = survey_sessions.get(response_id)
    if not session.get("survey_completed") and not (state and state.get("completed")):
        return redirect(url_for("home"))
    total = int(session.get("total_questions") or (state or {}).get("total") or QUESTIONS_PER_SESSION)
    lang = current_lang()
    txt = ui_strings(lang)
    html = render_template_string(
        THANKS_HTML,
        **page_context(
            thanks_body=txt["thanks_body"].format(n=total),
            debrief=build_debrief_context(response_id, lang),
        ),
    )
    response = make_response(html)
    return mark_participant_completed(response)


CHART_COLORS = {
    "original": "#64748b",
    "gemini": "#4285f4",
    "chatgpt": "#10a37f",
    "groq": "#f97316",
    "claude": "#d97757",
    "llm": "#818cf8",
}


def load_public_results():
    """Guncel anket formatindaki anonim yanitlar (5-way; eski 4-way dahil)."""
    rows = load_rows()
    current = [r for r in rows if r.get("survey_mode") in ("five_way", "four_way")]
    return current if current else rows


def build_stats_context(lang: str | None = None):
    lang = normalize_lang(lang or current_lang())
    txt = ui_strings(lang)
    labels = source_labels_for(lang)
    rows = load_public_results()
    report = analyze(rows)
    total = report["total_choices"]

    counts = {source: 0 for source in PREFERRED_SOURCES}
    for row in rows:
        source = row.get("chosen_source")
        if source in counts:
            counts[source] += 1

    source_count = report["source_trusted"]
    llm_count = report["llm_trusted"]
    source_pct = report["source_trusted_pct"]
    llm_pct = report["llm_trusted_pct"]

    all_rows = []
    for key in OPTION_ORDER:
        count = counts[key]
        pct = round((count / total) * 100, 1) if total else 0.0
        all_rows.append((labels[key], count, pct))

    winner = None
    if report["most_selected_llm"]:
        winner = labels[report["most_selected_llm"]]

    pie_data = {
        "labels": [txt["chart_source_label"], txt["chart_llm_label"]],
        "values": [source_count, llm_count],
        "colors": [CHART_COLORS["original"], CHART_COLORS["llm"]],
    }
    bar_data = {
        "labels": [labels[key] for key in OPTION_ORDER],
        "values": [counts[key] for key in OPTION_ORDER],
        "colors": [CHART_COLORS[key] for key in OPTION_ORDER],
    }

    return {
        "total": total,
        "participants": report["participants"],
        "source_count": source_count,
        "source_pct": source_pct,
        "llm_count": llm_count,
        "llm_pct": llm_pct,
        "all_rows": all_rows,
        "winner": winner,
        "pie_data": pie_data,
        "bar_data": bar_data,
        "chart_colors": [CHART_COLORS[key] for key in OPTION_ORDER],
        "bar_dataset_label": txt["bar_dataset"],
        "bar_tooltip_suffix": txt["bar_tooltip"],
    }


@app.get("/stats")
def stats():
    return render_template_string(
        STATS_HTML,
        **page_context(**build_stats_context()),
    )


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    host = os.getenv("HOST", "127.0.0.1")
    app.run(host=host, debug=debug, port=int(os.getenv("PORT", "5000")))
