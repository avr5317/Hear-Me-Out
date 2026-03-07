import asyncio
import wave
import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

PROMPT_FILE = "prompt.txt"
CHAR_FILE = "characteristics.txt"

client = genai.Client(
    api_key=API_KEY,
    http_options={"api_version": "v1alpha"}
)

def read_prompt(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    prompt = path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise ValueError(f"Prompt file is empty: {file_path}")
    return prompt

def read_characteristics(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Characteristics file not found: {file_path}")

    data = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid line in {file_path}: {line}")
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

    return {
        "bpm": int(data.get("bpm", 120)),
        "temperature": float(data.get("temperature", 1.0)),
        "duration": int(data.get("duration", 10)),
        "output_file": data.get("output_file", "lyria_output.wav")
    }

async def generate_audio(prompt_text: str, bpm: int, temperature: float, duration: int):
    audio_chunks = []

    async def receive_audio(session):
        async for message in session.receive():
            if message.server_content and message.server_content.audio_chunks:
                chunk = message.server_content.audio_chunks[0].data
                audio_chunks.append(chunk)
                print("Received audio chunk:", len(chunk))

    async with client.aio.live.music.connect(
        model="models/lyria-realtime-exp"
    ) as session:

        receive_task = asyncio.create_task(receive_audio(session))

        await session.set_weighted_prompts(
            prompts=[types.WeightedPrompt(text=prompt_text, weight=1.0)]
        )

        await session.set_music_generation_config(
            config=types.LiveMusicGenerationConfig(
                bpm=bpm,
                temperature=temperature
            )
        )

        await session.play()
        await asyncio.sleep(duration)
        receive_task.cancel()

    return b"".join(audio_chunks)

def save_wav(audio_data: bytes, filename: str):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(audio_data)
    print(f"Saved audio to {filename}")

if __name__ == "__main__":
    prompt_text = read_prompt(PROMPT_FILE)
    config = read_characteristics(CHAR_FILE)

    print("Using prompt:")
    print(prompt_text)
    print("-" * 50)
    print("Using characteristics:")
    print(config)
    print("-" * 50)

    audio_data = asyncio.run(
        generate_audio(
            prompt_text=prompt_text,
            bpm=config["bpm"],
            temperature=config["temperature"],
            duration=config["duration"]
        )
    )

    save_wav(audio_data, config["output_file"])