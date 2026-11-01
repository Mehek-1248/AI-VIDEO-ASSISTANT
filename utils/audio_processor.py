"""Acquire media and split it into Whisper-friendly audio chunks."""

from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import urlparse

CHUNK_LENGTH_MS = 10 * 60 * 1000
SUPPORTED_URL_SCHEMES = {"http", "https"}


def _is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in SUPPORTED_URL_SCHEMES and bool(parsed.netloc)


def _download_audio(url: str, output_dir: Path) -> Path:
    try:
        import yt_dlp
    except ImportError as exc:
        raise RuntimeError("yt-dlp is not installed. Install the project requirements first.") from exc

    output_template = str(output_dir / "source.%(ext)s")
    options = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(url, download=True)
            downloaded_path = Path(downloader.prepare_filename(info)).with_suffix(".wav")
    except Exception as exc:
        raise RuntimeError(f"Unable to download audio from the supplied URL: {exc}") from exc

    if not downloaded_path.exists():
        raise FileNotFoundError(f"Downloaded audio was not found at {downloaded_path}")
    return downloaded_path


def _resolve_source(source: str, work_dir: Path) -> Path:
    source = source.strip()
    if not source:
        raise ValueError("A YouTube URL or local media path is required.")

    if _is_url(source):
        return _download_audio(source, work_dir)

    media_path = Path(source).expanduser()
    if not media_path.is_file():
        raise FileNotFoundError(f"Local media file was not found: {media_path}")
    return media_path


def _export_chunks(media_path: Path, output_dir: Path) -> list[str]:
    try:
        from pydub import AudioSegment
    except ImportError as exc:
        raise RuntimeError("pydub is not installed. Install the project requirements first.") from exc

    try:
        audio = AudioSegment.from_file(media_path)
    except Exception as exc:
        raise RuntimeError(
            "Unable to read the media file. Check that FFmpeg is installed and available on PATH."
        ) from exc

    if len(audio) == 0:
        raise ValueError("The supplied media file contains no audio.")

    chunks: list[str] = []
    for index, start in enumerate(range(0, len(audio), CHUNK_LENGTH_MS), start=1):
        chunk_path = output_dir / f"chunk_{index:03d}.wav"
        audio[start : start + CHUNK_LENGTH_MS].set_channels(1).export(
            chunk_path,
            format="wav",
            parameters=["-ar", "16000"],
        )
        chunks.append(str(chunk_path))

    return chunks


def process_input(source: str) -> list[str]:
    """Download or load media and return temporary 16 kHz mono WAV chunks.

    The returned paths remain valid for the lifetime of the current process.
    """
    work_dir = Path(tempfile.mkdtemp(prefix="ai_video_assistant_"))
    media_path = _resolve_source(source, work_dir)
    return _export_chunks(media_path, work_dir)
