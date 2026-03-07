import os
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("ELEVENLABS_API_KEY")
OUTPUT_FILE = BASE_DIR / "eleven_song.mp3"

if not API_KEY:
    raise ValueError("Missing ELEVENLABS_API_KEY in .env")

client = ElevenLabs(api_key=API_KEY)

composition_plan = {
    "positive_global_styles": [
        "modern Bollywood wedding dance song",
        "female vocalist with clear melodic tone",
        "Hindi pop vocal delivery",
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
                "build anticipation",
                "dhol groove begins"
            ],
            "negative_local_styles": [
                "lead vocals",
                "rap",
                "harsh singing"
            ],
            "duration_ms": 6000,
            "lines": []
        },
        {
            "section_name": "Verse 1",
            "positive_local_styles": [
                "female lead vocals clearly begin here",
                "melodic and expressive",
                "romantic Bollywood phrasing"
            ],
            "negative_local_styles": [
                "instrumental only",
                "spoken word",
                "male lead vocals"
            ],
            "duration_ms": 12000,
            "lines": [
                "Aaja re sajna, dil yeh pukare",
                "Raat yeh mehki, sapne sawaren"
            ]
        },
        {
            "section_name": "Chorus",
            "positive_local_styles": [
                "big catchy chorus",
                "strong memorable hook",
                "full festive arrangement",
                "female vocals front and center"
            ],
            "negative_local_styles": [
                "instrumental only",
                "spoken word",
                "low energy"
            ],
            "duration_ms": 12000,
            "lines": [
                "Nach le saath mere, dil se dil mila",
                "Aaj ki raat hai, pyaar ka silsila"
            ]
        }
    ]
}

track = client.music.compose(
    composition_plan=composition_plan
)

with open(OUTPUT_FILE, "wb") as f:
    for chunk in track:
        f.write(chunk)

print(f"Saved song to {OUTPUT_FILE}")