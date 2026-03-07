from pathlib import Path

STORY_FILE = "story.txt"
LYRICS_FILE = "lyrics.txt"

def read_story(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Story file not found: {file_path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Story file is empty: {file_path}")
    return text

def generate_lyrics_from_story(story: str) -> str:
    """
    Simple rule-based placeholder version.
    Later you can replace this with an actual LLM API call.
    """
    story_lower = story.lower()

    if "wedding" in story_lower or "married" in story_lower:
        theme = "wedding"
    elif "breakup" in story_lower or "lost love" in story_lower:
        theme = "heartbreak"
    else:
        theme = "romantic"

    if "joyful" in story_lower or "festive" in story_lower:
        mood = "joyful"
    elif "sad" in story_lower or "heartbroken" in story_lower:
        mood = "sad"
    else:
        mood = "emotional"

    if theme == "wedding" and mood == "joyful":
        return """[Verse]
Aaja re sajna, sapna saj gaya
Dil ka yeh rishta, roshan ho gaya

[Chorus]
Nach le saath mere, khushiyon ka yeh din
Pyaar ki mehfil mein, chamke mera mann
"""
    elif theme == "heartbreak":
        return """[Verse]
Raat ke saaye mein, naam tera raha
Dil ki khamoshi mein, dard hi raha

[Chorus]
Toota sa yeh dil hai, phir bhi yaad teri
Chandni bhi pooche, kahan gayi khushi meri
"""
    else:
        return """[Verse]
Dil ne jo mehsoos kiya, kehna chahta hai
Sapnon ka yeh raasta, tujhmein milta hai

[Chorus]
Saath tera lage, jaise roshni ka jahaan
Pyaar ka yeh naghma, gunje har samaa
"""

def save_lyrics(lyrics: str, file_path: str):
    Path(file_path).write_text(lyrics, encoding="utf-8")
    print(f"Lyrics saved to {file_path}")

if __name__ == "__main__":
    story = read_story(STORY_FILE)
    lyrics = generate_lyrics_from_story(story)
    print("Generated Lyrics:\n")
    print(lyrics)
    save_lyrics(lyrics, LYRICS_FILE)