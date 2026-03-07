import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name == "test_lyria" else BASE_DIR

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("ELEVENLABS_API_KEY")
LYRICS_FILE = BASE_DIR / "lyrics.txt"
OUTPUT_FILE = BASE_DIR / "eleven_song.mp3"

if not API_KEY:
    raise ValueError("Missing ELEVENLABS_API_KEY in .env")

client = ElevenLabs(api_key=API_KEY)

def read_lyrics(file_path: Path) -> dict:
    if not file_path.exists():
        raise FileNotFoundError(f"Lyrics file not found: {file_path}")

    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Lyrics file is empty: {file_path}")

    verse_lines = []
    chorus_lines = []
    current_section = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lower = line.lower()
        if lower == "[verse]":
            current_section = "verse"
            continue
        elif lower == "[chorus]":
            current_section = "chorus"
            continue

        if current_section == "verse":
            verse_lines.append(line)
        elif current_section == "chorus":
            chorus_lines.append(line)

    if not verse_lines or not chorus_lines:
        raise ValueError("lyrics.txt must contain both [Verse] and [Chorus] sections")

    return {
        "verse": verse_lines,
        "chorus": chorus_lines
    }

lyrics = read_lyrics(LYRICS_FILE)

composition_plan = {
    "positive_global_styles": [
        "modern Bollywood wedding dance song",
        "female vocalist with clear melodic tone",
        "romantic cinematic pop",
        "catchy chorus",
        "dhol and tabla percussion",
        "bright violins",
        "celebratory energy",
        "polished studio production",
        "120 BPM"
    ],
    "negative_global_styles": [
        "instrumental only",
        "spoken word",
        "a cappella",
        "dark",
        "aggressive metal"
    ],
    "sections": [
        {
            "section_name": "Intro",
            "positive_local_styles": [
                "instrumental intro",
                "build anticipation"
            ],
            "negative_local_styles": [
                "lead vocals",
                "rap"
            ],
            "duration_ms": 5000,
            "lines": []
        },
        {
            "section_name": "Verse 1",
            "positive_local_styles": [
                "female lead vocals clearly begin here",
                "melodic and expressive",
                "romantic phrasing"
            ],
            "negative_local_styles": [
                "instrumental only",
                "spoken word"
            ],
            "duration_ms": 12000,
            "lines": lyrics["verse"]
        },
        {
            "section_name": "Chorus",
            "positive_local_styles": [
                "big catchy chorus",
                "female vocals front and center",
                "festive wedding energy"
            ],
            "negative_local_styles": [
                "instrumental only",
                "low energy"
            ],
            "duration_ms": 12000,
            "lines": lyrics["chorus"]
        }
    ]
}

track = client.music.compose(composition_plan=composition_plan)

with open(OUTPUT_FILE, "wb") as f:
    for chunk in track:
        f.write(chunk)

print(f"Saved song to {OUTPUT_FILE}")