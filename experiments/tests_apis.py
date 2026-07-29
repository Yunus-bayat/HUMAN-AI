"""API connectivity tests for ChatGPT, Gemini, and Groq."""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai
from groq import Groq

load_dotenv()


def _mask(key: Optional[str]) -> str:
    if not key:
        return "(yok)"
    if len(key) < 10:
        return "***"
    return f"{key[:4]}...{key[-4:]}"


def test_openai() -> bool:
    print("OpenAI (ChatGPT) test ediliyor...")
    try:
        api_key = os.getenv("CHATGPT_API_KEY") or os.getenv("OPENAI_API_KEY")
        print(f"  Key: {_mask(api_key)}")
        if not api_key:
            print("CHATGPT_API_KEY / OPENAI_API_KEY bulunamadi!")
            return False

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello in one word."}],
            max_tokens=5,
        )
        print(f"OpenAI basarili! Yanit: {response.choices[0].message.content.strip()}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"OpenAI hatasi: {exc}")
        return False


def test_gemini() -> bool:
    print("\nGoogle Gemini test ediliyor...")
    try:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        print(f"  Key: {_mask(api_key)}")
        if not api_key:
            print("GEMINI_API_KEY / GOOGLE_API_KEY bulunamadi!")
            return False

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")
        response = model.generate_content("Say hello in one word.")
        print(f"Gemini basarili! Yanit: {response.text.strip()}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"Gemini hatasi: {exc}")
        return False


def test_groq() -> bool:
    print("\nGroq test ediliyor...")
    try:
        api_key = os.getenv("GROQ_API_KEY")
        print(f"  Key: {_mask(api_key)}")
        if not api_key:
            print("GROQ_API_KEY bulunamadi!")
            return False

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello in one word."}],
            max_tokens=5,
        )
        print(f"Groq basarili! Yanit: {response.choices[0].message.content.strip()}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"Groq hatasi: {exc}")
        return False


if __name__ == "__main__":
    print("API baglanti testleri baslatiliyor...\n" + "-" * 40)
    results = [test_openai(), test_gemini(), test_groq()]
    print("-" * 40)
    print(f"Tamamlanan basarili test: {sum(results)}/3")
