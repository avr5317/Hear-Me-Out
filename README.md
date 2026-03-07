# Hear Me Out

**Turn a story into a song. No musical talent required.**

Hear Me Out takes a short description of a memory, a moment or a feeling and turns it into a finished track with original lyrics, AI-sung vocals and instrumentation. Under the hood it is a four stage AI pipeline that chains Claude Sonnet, Gemini and ElevenLabs, exposed through a FastAPI backend that keeps a session for every song so you can keep refining it.

Built at the Frontier Hackathon (sponsored by Google DeepMind) in March 2026, within a 48 hour window.

---

## How it works

You write a few sentences. The pipeline passes one shared context object through four stages, and every stage reads what the earlier ones produced.

| Stage | Model | What it does |
|-------|-------|--------------|
| 1. Narrative | Claude Sonnet 4 | Expands the input into a short, sensory story that captures the mood and atmosphere |
| 2. Musical features | Gemini 2.5 Flash | Reads the narrative and returns structured JSON: tempo, genre, mood, instruments, scale, chord progression, energy, dynamics and duration |
| 3. Lyrics | Claude Sonnet 4 | Writes a verse and a chorus that fit the story, the mood and the tempo |
| 4. Music | Claude Sonnet 4 and ElevenLabs Music API | Claude builds a section by section composition plan from the story, features and lyrics, and ElevenLabs renders it as audio with vocals |

After the four stages, the pipeline also saves a PDF summary of the narrative and the musical features for that round.

If Gemini returns JSON that cannot be parsed, the pipeline falls back to a safe set of default features and keeps going, so one bad response does not stop a run.

### Refining a song

Each round of feedback is saved to a history. When you refine a song, the whole pipeline runs again, and the prompts include the original request, the current narrative, the current features and every earlier piece of feedback. For example, "make it slower and sadder" changes the narrative, the features, the lyrics and the audio together, so the song stays coherent.

---

## Architecture

```
user input
    |
    v
Orchestrator  --->  PipelineContext (narrative, features, lyrics, audio, history)
    |
    +--> narrative.py          Claude Sonnet   story expansion
    +--> analyzer.py           Gemini          musical features as JSON
    +--> lyrics_generator.py   Claude Sonnet   verse and chorus
    +--> eleven_generator.py   Claude + ElevenLabs   composition plan and audio
    +--> pdf_generator.py      PDF summary of the round
```

- **`Orchestrator`** runs the stages in order and handles refinement.
- **`PipelineContext`** is the single object that flows through every stage. It holds the narrative, the musical features, the lyrics, the output files, the iteration number and the feedback history.
- **`MusicalFeatures`** is a typed dataclass, so every stage works with the same fields.
- **FastAPI backend** keeps one orchestrator per session ID, so a user can come back to the same song and refine it.

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/process` | Start a session. Body: `text`, optional `session_id`, optional `generator`. Returns the narrative, lyrics, features and an audio URL |
| `POST` | `/refine` | Refine an existing session. Body: `feedback`, `session_id`. Runs the pipeline again with the accumulated context |
| `GET` | `/status/{session_id}` | Returns the iteration number, whether a narrative exists, the current features, the output files and the history length |
| `GET` | `/audio/{filename}` | Serves a generated audio file from the `output` folder |
| `GET` | `/` | Serves the web page |

---

## Tech stack

| Area | Technology |
|------|------------|
| Language | Python |
| Backend | FastAPI, Pydantic |
| Language models | Claude Sonnet 4 (Anthropic API), Gemini 2.5 Flash (Google Generative AI) |
| Audio | ElevenLabs Music API |
| Documents | ReportLab (PDF summary) |
| Frontend | A single HTML page with an audio player and lyrics display |

---

## Getting started

### Prerequisites

- Python 3
- An [Anthropic](https://console.anthropic.com), a [Google AI Studio](https://aistudio.google.com) and an [ElevenLabs](https://elevenlabs.io) API key

### Install

```bash
git clone <your-repo-url>
cd music-ai
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn anthropic google-generativeai elevenlabs python-dotenv reportlab
```

### Configure

Create a `.env` file in the project root. It is listed in `.gitignore`, so it is never committed.

```
ANTHROPIC_API_KEY=your-key
GEMINI_API_KEY=your-key
ELEVENLABS_API_KEY=your-key
```

### Run the web app

Start the server from the project root, because generated files are written to an `output` folder relative to where you run it:

```bash
uvicorn user_input.backend.main:app --reload
```

Open `http://localhost:8000`, describe a moment, and play the result.

### Run from the command line

```bash
python main.py
```

Describe your musical vision, then use `f` to give feedback and refine the song, `s` to show the current state, or `q` to quit.

### Choose the audio generator

By default, audio comes from ElevenLabs. Set `MUSIC_GENERATOR=local` to use the built-in synthesizer in `generator.py` instead. It renders a simple WAV file from the scale and chord progression, with no API call.

Generated files go to `output/` as `music_v<round>.mp3` and `narrative_v<round>.pdf`.

---

## Project structure

```
music-ai/
├── main.py                   # Command line interface with a feedback loop
├── orchestrator.py           # Runs the stages and handles refinement
├── context.py                # PipelineContext and MusicalFeatures
├── narrative.py              # Stage 1: narrative expansion (Claude)
├── analyzer.py               # Stage 2: musical features as JSON (Gemini)
├── lyrics_generator.py       # Stage 3: lyrics (Claude)
├── eleven_generator.py       # Stage 4: composition plan and audio (Claude and ElevenLabs)
├── generator.py              # Local fallback synthesizer
├── pdf_generator.py          # PDF summary of each round
├── user_input/
│   ├── backend/main.py       # FastAPI app and session handling
│   └── frontend/index.html   # Web page
└── test_lyria/               # Early experiments with Lyria and ElevenLabs
```

---

## Known limitations

1. **Sessions live in memory.** They reset when the server restarts. Next step: store them in a database.
2. **The web page calls `/process` only.** Refinement is available through `POST /refine` and the command line tool. Next step: add a refinement panel to the page.
3. **Songs are short.** The pipeline asks for 10 to 30 seconds of music. Next step: support longer structures with a bridge and a second verse.
4. **No automated tests.** `test_lyria/` holds manual experiments. Next step: unit tests for the context handling and the JSON fallback.
5. **CORS is open to every origin,** which suits local development. Restrict it before deploying.

