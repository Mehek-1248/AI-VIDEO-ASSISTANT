# AI Video Assistant

The project accepts a YouTube URL or local media file, extracts audio, transcribes it, generates a title and summary, extracts meeting insights, and provides transcript-grounded question answering.

## Setup

Use Python 3.10 or 3.11, install FFmpeg, create a virtual environment, and install the dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r Requirements.txt
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
