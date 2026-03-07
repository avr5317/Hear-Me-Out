def analyze_text(text):

    features = {
        "genre": "ambient",
        "tempo": 80,
        "mood": "calm",
        "instrument": "piano"
    }

    if "dark" in text:
        features["mood"] = "dark"

    if "fast" in text:
        features["tempo"] = 120

    if "cinematic" in text:
        features["genre"] = "cinematic"

    return features