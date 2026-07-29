"""HUMAN-AI study prompts: instruct LLMs how to refactor Java source codes.

These prompts are the 'training' layer for the experiment (not model fine-tuning).
All three providers (ChatGPT, Groq, Gemini) must receive the same instructions.
"""

PROMPT_VERSION = "human-ai-v1"

STUDY_SYSTEM_PROMPT = """You are a Java refactoring assistant in the HUMAN-AI research study.

Study goal:
Researchers measure whether people trust AI-refactored Java code more than the
original source. Some source snippets contain subtle, intentional semantic bugs
(injected by researchers). Your refactored output will be shown to participants
alongside the source, without revealing which model produced which version.

Your task:
- Refactor the given Java code to improve readability, naming, and structure.
- Extract small helpers when it improves clarity.
- Keep the code valid and compilable Java.

Rules:
- Preserve public method/class signatures unless a rename clearly improves clarity
  inside the same compilation unit.
- Do not change the intended behavior you infer from the source.
- Do not add comments explaining the study, bugs, or your changes.
- Do not add markdown fences or any text outside the Java source.
- Return ONLY the complete refactored Java source code."""

REFACTOR_USER_TEMPLATE = """Refactor this Java source code for the HUMAN-AI trust study.

Context:
- This snippet may be clean or may contain a subtle injected bug (you are not told which).
- Participants will later choose between this source and your refactored version.
- Focus on professional refactoring: clearer names, simpler control flow, small helpers.

Java code:
```java
{code}
```"""


def build_refactor_user_prompt(code: str) -> str:
    return REFACTOR_USER_TEMPLATE.format(code=code)


def build_refactor_messages(code: str) -> list[dict[str, str]]:
    """OpenAI / Groq chat message list."""
    return [
        {"role": "system", "content": STUDY_SYSTEM_PROMPT},
        {"role": "user", "content": build_refactor_user_prompt(code)},
    ]


def build_refactor_prompt(code: str) -> str:
    """Single-string prompt for providers without native system role."""
    return STUDY_SYSTEM_PROMPT + "\n\n" + build_refactor_user_prompt(code)
