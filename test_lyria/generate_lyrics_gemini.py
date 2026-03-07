import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if BASE_DIR.name == "test_lyria" else BASE_DIR

load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

STORY_FILE = BASE_DIR / "story.txt"
LYRICS_FILE = BASE_DIR / "lyrics.txt"

client = genai.Client(api_key=GEMINI_API_KEY)

def read_story(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"Story file not found: {file_path}")
    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Story file is empty: {file_path}")
    return text

def build_prompt(story: str) -> str:
    return f"""
You are a professional lyricist for film music.

Read the story below and write ORIGINAL song lyrics inspired by it.

Requirements:
- Style: Bollywood romantic wedding song
- Mood: joyful, emotional, cinematic, festive
- Voice: female lead vocals
- Output ONLY these sections exactly:
[Verse]
...2 to 4 lines...

[Chorus]
...2 to 4 lines...
- Keep lyrics short, catchy, singable, and emotionally clear
- Do not explain anything
- Do not add notes
- Do not add extra sections
- Prefer Hindi/Urdu-flavored romanized lyrics that are easy to sing

Story:
{story}
""".strip()

def save_lyrics(text: str, file_path: Path):
    file_path.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"Saved lyrics to {file_path}")

def main():
    story = read_story(STORY_FILE)
    prompt = build_prompt(story)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    lyrics = response.text.strip()
    print("Generated lyrics:\n")
    print(lyrics)
    print()
    save_lyrics(lyrics, LYRICS_FILE)

if __name__ == "__main__":
    main()