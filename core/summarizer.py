"""Generate a title and concise summary from a transcript."""

from __future__ import annotations

from core.llm import invoke_text


def _require_transcript(transcript: str) -> str:
    transcript = transcript.strip()
    if not transcript:
        raise ValueError("A non-empty transcript is required.")
    return transcript


def generate_title(transcript: str) -> str:
    transcript = _require_transcript(transcript)
    return invoke_text(
        "Create a short, specific title for this recording. Return only the title, "
        "without quotation marks or a prefix.\n\nTranscript:\n" + transcript
    )


def summarize(transcript: str) -> str:
    transcript = _require_transcript(transcript)
    return invoke_text(
        "Summarize this recording in 5 to 8 concise bullet points. Preserve important "
        "names, dates, numbers, decisions, and technical details. Return only the bullets.\n\n"
        "Transcript:\n" + transcript
    )
