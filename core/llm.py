"""Shared LLM configuration for analysis and question answering."""

from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()

    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required when LLM_PROVIDER is 'groq'.")
        try:
            from langchain_groq import ChatGroq
        except ImportError as exc:
            raise RuntimeError("langchain-groq is not installed.") from exc
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            temperature=0,
            api_key=api_key,
        )

    if provider == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY is required when LLM_PROVIDER is 'mistral'.")
        try:
            from langchain_mistralai import ChatMistralAI
        except ImportError as exc:
            raise RuntimeError("langchain-mistralai is not installed.") from exc
        return ChatMistralAI(
            model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
            temperature=0,
            api_key=api_key,
        )

    raise ValueError("LLM_PROVIDER must be either 'groq' or 'mistral'.")


def invoke_text(prompt: str) -> str:
    response = get_llm().invoke(prompt)
    content = getattr(response, "content", response)
    if not isinstance(content, str):
        content = str(content)
    return content.strip()
