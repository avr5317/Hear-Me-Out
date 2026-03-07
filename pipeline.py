from analyzer import analyze_text
from generator import generate_music

def run_pipeline(prompt):

    features = analyze_text(prompt)

    print("Features:", features)

    music_file = generate_music(features)

    return music_file