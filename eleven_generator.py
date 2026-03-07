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


def _build_composition_plan(context):
    """Use Claude to build an ElevenLabs composition plan from narrative + features."""
    client = _get_claude_client()
    features = context.musical_features.to_dict()

    prompt = f"""You are a music producer creating a composition plan for the ElevenLabs Music API.

Given the narrative and musical features below, create a JSON composition plan with this exact structure:
{{
    "positive_global_styles": [list of 5-8 style descriptors like "dark cinematic piano", "slow tempo", "melancholy strings"],
    "negative_global_styles": [list of 3-5 things to avoid],
    "sections": [
        {{
            "section_name": "Main",
            "positive_local_styles": [3-5 style descriptors for this section],
            "negative_local_styles": [2-3 things to avoid],
            "duration_ms": {context.musical_features.duration * 1000},
            "lines": []
        }}
    ]
}}

Include the BPM ({features['tempo']} BPM) in positive_global_styles.
Match the mood, genre, instruments, and energy from the features.

Narrative:
{context.narrative[:500]}

Musical features:
{json.dumps(features, indent=2)}

Return ONLY the JSON object, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    return json.loads(text)


def generate_music_eleven(context):
    """Generate music using ElevenLabs Music API."""
    os.makedirs("output", exist_ok=True)

    print("  Building ElevenLabs composition plan...")
    composition_plan = _build_composition_plan(context)
    print(f"  Styles: {composition_plan.get('positive_global_styles', [])}")

    print("  Generating music with ElevenLabs...")
    eleven_client = _get_eleven_client()
    track = eleven_client.music.compose(composition_plan=composition_plan)

    output_path = f"output/music_v{context.iteration}.mp3"
    with open(output_path, "wb") as f:
        for chunk in track:
            f.write(chunk)

    print(f"  Saved: {output_path}")
    context.audio_file = output_path
    return context
