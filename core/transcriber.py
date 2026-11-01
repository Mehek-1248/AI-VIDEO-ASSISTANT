"""Speech-to-text adapters for local Whisper and Sarvam AI."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import requests


@lru_cache(maxsize=1)
def _load_whisper_model(model_name: str):
    try:
        import whisper
    except ImportError as exc:
        raise RuntimeError(
            "Whisper is not installed. Install the project requirements before using English transcription."
        ) from exc

    return whisper.load_model(model_name)


def _transcribe_with_whisper(audio_path: str) -> str:
    model_name = os.getenv("WHISPER_MODEL", "tiny")
    model = _load_whisper_model(model_name)
    result = model.transcribe(audio_path, language="en", fp16=False)
    return result.get("text", "").strip()


def _transcribe_with_sarvam(audio_path: str) -> str:
    api_key = os.getenv("SARVAM_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("SARVAM_API_KEY is required when language is 'hinglish'.")

    endpoint = "https://api.sarvam.ai/speech-to-text"
    model = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")
    try:
        with Path(audio_path).open("rb") as audio_file:
            response = requests.post(
                endpoint,
                headers={"api-subscription-key": api_key},
                files={"file": (Path(audio_path).name, audio_file, "audio/wav")},
                data={"model": model},
                timeout=120,
            )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Sarvam transcription failed: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Sarvam returned an invalid JSON response.") from exc

    transcript = payload.get("transcript", "")
    if not isinstance(transcript, str):
        raise RuntimeError("Sarvam returned an unexpected transcription response.")
    return transcript.strip()


def transcribe_all(chunks: list[str], language: str = "english") -> str:
    """Transcribe all audio chunks and return one ordered transcript."""
    if not chunks:
        raise ValueError("No audio chunks were supplied for transcription.")

    normalized_language = language.strip().lower()
    if normalized_language not in {"english", "hinglish"}:
        raise ValueError("Language must be either 'english' or 'hinglish'.")

    transcribe = (
        _transcribe_with_sarvam
        if normalized_language == "hinglish"
        else _transcribe_with_whisper
    )
    transcripts = [transcribe(chunk) for chunk in chunks]
    transcript = "\n".join(part for part in transcripts if part)
    if not transcript:
        raise RuntimeError("Transcription completed, but no speech was detected.")
    return transcript
