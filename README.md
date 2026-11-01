# AI Video Assistant

The project accepts a YouTube URL or local media file, extracts audio, transcribes it, generates a title and summary, extracts meeting insights, and provides transcript-grounded question answering.

## Setup

Use Python 3.10 or 3.11, install FFmpeg, create a virtual environment, and install the dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and provide the API keys needed by the selected providers.

## Run

```powershell
streamlit run app.py
```

The CLI is also available:

```powershell
python main.py
```

## Offline checks

```powershell
python -m unittest discover -s tests -v
```

FFmpeg must be installed separately and available through `ffmpeg -version`.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create an app at [Streamlit Community Cloud](https://share.streamlit.io/) using `app.py` as the entry point and Python 3.11.
3. Add the required provider credentials in the app's **Settings → Secrets**. For the default Groq provider:

   ```toml
   LLM_PROVIDER = "groq"
   GROQ_API_KEY = "your-groq-api-key"
   GROQ_MODEL = "openai/gpt-oss-20b"
   WHISPER_MODEL = "tiny"
   ```

   Add `SARVAM_API_KEY` to enable Hinglish transcription. Keep credentials out of GitHub.

The app uses FFmpeg, installed from `packages.txt`. Initial transcription and retrieval-model downloads may take a few minutes. The deployed app can access YouTube URLs, but not file paths on your computer.
