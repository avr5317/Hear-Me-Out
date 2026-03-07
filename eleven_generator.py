import json
import os
import anthropic
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

load_dotenv(override=True)


def _get_eleven_client():
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set.")
    return ElevenLabs(api_key=api_key)


def _get_claude_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set.")
    return anthropic.Anthropic(api_key=api_key)


def _parse_lyrics(lyrics_text):
    """Parse lyrics text into verse and chorus line lists."""
    verse_lines = []
    chorus_lines = []
    current_section = None

    for raw_line in lyrics_text.splitlines():
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

    return verse_lines, chorus_lines


def _build_composition_plan(context):
    """Use Claude to build an ElevenLabs composition plan with vocals from narrative + features + lyrics."""
    client = _get_claude_client()
    features = context.musical_features.to_dict()

    verse_lines, chorus_lines = _parse_lyrics(context.lyrics)
    has_lyrics = bool(verse_lines and chorus_lines)

    # Calculate section durations from total duration
    total_ms = features["duration"] * 1000
    if has_lyrics:
        intro_ms = min(5000, total_ms // 6)
        remaining = total_ms - intro_ms
        verse_ms = remaining // 2
        chorus_ms = remaining - verse_ms
    else:
        intro_ms = total_ms
        verse_ms = 0
        chorus_ms = 0

    prompt = f"""You are a music producer creating a composition plan for the ElevenLabs Music API.

Given the narrative, musical features, and lyrics below, create a JSON composition plan.
The plan must have this exact structure:

{{
    "positive_global_styles": [list of 5-8 style descriptors including vocalist type, genre, instruments, BPM],
    "negative_global_styles": [list of 3-5 things to avoid]
}}

Include these in positive_global_styles:
- A vocalist description (e.g. "female vocalist with clear melodic tone" or "male vocalist with deep emotional delivery")
- The genre: {features['genre']}
- Key instruments: {', '.join(features['instruments'])}
- "{features['tempo']} BPM"
- The mood: {features['mood']}
- Production quality descriptor

Include in negative_global_styles:
- Things that conflict with the mood/genre

Narrative:
{context.narrative[:300]}

Return ONLY the JSON object with positive_global_styles and negative_global_styles. No other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    styles = json.loads(text)

    # Build sections
    sections = []

    sections.append({
        "section_name": "Intro",
        "positive_local_styles": ["instrumental intro", "build anticipation", "set the mood"],
        "negative_local_styles": ["lead vocals", "rap"],
        "duration_ms": intro_ms,
        "lines": [],
    })

    if has_lyrics:
        sections.append({
            "section_name": "Verse",
            "positive_local_styles": [
                "lead vocals clearly begin here",
                "melodic and expressive",
                f"{features['mood']} vocal delivery",
            ],
            "negative_local_styles": ["instrumental only", "spoken word"],
            "duration_ms": verse_ms,
            "lines": verse_lines,
        })
        sections.append({
            "section_name": "Chorus",
            "positive_local_styles": [
                "big catchy chorus",
                "vocals front and center",
                "strong memorable hook",
                "full arrangement",
            ],
            "negative_local_styles": ["instrumental only", "low energy"],
            "duration_ms": chorus_ms,
            "lines": chorus_lines,
        })

    styles["sections"] = sections
    return styles


def generate_music_eleven(context):
    """Generate music with vocals using ElevenLabs Music API."""
    os.makedirs("output", exist_ok=True)

    print("  Building ElevenLabs composition plan with lyrics...")
    composition_plan = _build_composition_plan(context)
    print(f"  Styles: {composition_plan.get('positive_global_styles', [])}")
    print(f"  Sections: {[s['section_name'] for s in composition_plan['sections']]}")

    print("  Generating music + vocals with ElevenLabs...")
    eleven_client = _get_eleven_client()
    track = eleven_client.music.compose(composition_plan=composition_plan)

    output_path = f"output/music_v{context.iteration}.mp3"
    with open(output_path, "wb") as f:
        for chunk in track:
            f.write(chunk)

    print(f"  Saved: {output_path}")
    context.audio_file = output_path
    return context
