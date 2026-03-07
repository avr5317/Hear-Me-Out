import json
import os
from google import genai
from dotenv import load_dotenv
from context import MusicalFeatures

load_dotenv(override=True)


def _get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Add it to your .env file or export it as an environment variable."
        )
    return genai.Client(api_key=api_key)


def extract_musical_features(context):
    """Analyze narrative context and extract structured musical parameters using Gemini."""
    client = _get_client()

    prompt = f"""Analyze the following narrative and extract musical parameters.
Return ONLY a valid JSON object with these fields:
- tempo (integer, 40-200 BPM)
- genre (string)
- mood (string)
- instruments (list of strings)
- scale (string, e.g. "C minor", "D major")
- chord_progression (list of chord strings, 4-8 chords)
- energy (float 0.0-1.0, where 0 is very calm and 1 is very intense)
- dynamics (string: "whisper", "soft", "moderate", "loud", "explosive")

Narrative:
{context.narrative}

Current musical features for reference (adjust based on narrative):
{context.musical_features.to_json()}

Return ONLY the JSON object, no other text."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    text = response.text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    features_dict = json.loads(text)
    context.musical_features = MusicalFeatures.from_dict(features_dict)
    return context
