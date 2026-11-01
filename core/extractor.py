"""Extract structured meeting information from a transcript."""

from __future__ import annotations

from core.llm import invoke_text


def _extract(transcript: str, category: str, instruction: str) -> str:
    transcript = transcript.strip()
    if not transcript:
        raise ValueError("A non-empty transcript is required.")
    return invoke_text(
        f"Extract {category} from the transcript below. {instruction} "
        "If none exist, return exactly: None found. Return only the resulting list.\n\n"
        f"Transcript:\n{transcript}"
    )


def extract_action_items(transcript: str) -> str:
    return _extract(
        transcript,
        "action items",
        "Include the responsible person and deadline when stated.",
    )


def extract_key_decisions(transcript: str) -> str:
    return _extract(
        transcript,
        "key decisions",
        "Include the chosen option and the reason when stated.",
    )


def extract_questions(transcript: str) -> str:
    return _extract(
        transcript,
        "open questions",
        "Include unresolved questions and missing information that needs follow-up.",
    )
