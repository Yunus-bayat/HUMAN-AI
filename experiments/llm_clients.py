"""Shared LLM client helpers for Groq, Gemini, ChatGPT, and Claude."""

from __future__ import annotations

import os
import re

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
import google.generativeai as genai

from study_prompts import (
    STUDY_SYSTEM_PROMPT,
    build_refactor_messages,
    build_refactor_user_prompt,
)

load_dotenv()

# Haiku 4.5: en ucuz Claude tier, kod refaktoru icin yeterli kalite (~$1/$5 per 1M tokens).
# 3.5 modelleri API'den kaldirildi (2026-02).
CLAUDE_REFACTOR_MODEL = "claude-haiku-4-5-20251001"
# Dataset'teki Java parcalari kisa; uzun cevaplari sinirlayarak gereksiz output token harcamasini onler.
CLAUDE_REFACTOR_MAX_TOKENS = 2048


def _clean_code(text: str) -> str:
    text = text.strip()
    fence = re.match(r"^```(?:java)?\s*([\s\S]*?)\s*```$", text, re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return text


def get_chatgpt_key():
    return os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY")


def get_groq_key():
    return os.getenv("GROQ_API_KEY")


def get_gemini_key():
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def get_claude_key():
    return os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")


def refactor_with_chatgpt(code: str, model: str = "gpt-4o-mini") -> str:
    api_key = get_chatgpt_key()
    if not api_key:
        raise RuntimeError("CHATGPT_API_KEY / OPENAI_API_KEY bulunamadi")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=build_refactor_messages(code),
        temperature=0.2,
    )
    return _clean_code(response.choices[0].message.content or "")


def refactor_with_groq(code: str, model: str = "llama-3.3-70b-versatile") -> str:
    api_key = get_groq_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY bulunamadi")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=build_refactor_messages(code),
        temperature=0.2,
    )
    return _clean_code(response.choices[0].message.content or "")


def refactor_with_gemini(code: str, model: str = "gemini-flash-lite-latest") -> str:
    api_key = get_gemini_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY / GOOGLE_API_KEY bulunamadi")
    genai.configure(api_key=api_key)
    gemini = genai.GenerativeModel(
        model_name=model,
        system_instruction=STUDY_SYSTEM_PROMPT,
    )
    user_prompt = build_refactor_user_prompt(code)
    response = gemini.generate_content(user_prompt)
    return _clean_code(getattr(response, "text", "") or "")


def refactor_with_claude(
    code: str,
    model: str = CLAUDE_REFACTOR_MODEL,
    max_tokens: int = CLAUDE_REFACTOR_MAX_TOKENS,
) -> str:
    api_key = get_claude_key()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY / CLAUDE_API_KEY bulunamadi")
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=STUDY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_refactor_user_prompt(code)}],
        temperature=0.2,
    )
    parts = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return _clean_code("".join(parts))


PROVIDERS = {
    "chatgpt": refactor_with_chatgpt,
    "groq": refactor_with_groq,
    "gemini": refactor_with_gemini,
    "claude": refactor_with_claude,
}
