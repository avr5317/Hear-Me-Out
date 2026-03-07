import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestrator import Orchestrator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions keyed by session ID
sessions: dict[str, Orchestrator] = {}


class ProcessRequest(BaseModel):
    text: str
    session_id: str = "default"


class FeedbackRequest(BaseModel):
    feedback: str
    session_id: str = "default"


@app.post("/process")
def process(request: ProcessRequest):
    """Start a new pipeline session from user input."""
    orchestrator = Orchestrator(request.text)
    context = orchestrator.run_full_cycle()
    sessions[request.session_id] = orchestrator

    return {
        "session_id": request.session_id,
        "iteration": context.iteration,
        "narrative": context.narrative,
        "musical_features": context.musical_features.to_dict(),
        "audio_file": context.audio_file,
        "pdf_file": context.pdf_file,
    }


@app.post("/refine")
def refine(request: FeedbackRequest):
    """Refine an existing session with user feedback."""
    orchestrator = sessions.get(request.session_id)
    if not orchestrator:
        return {"error": f"No active session '{request.session_id}'. Call /process first."}

    context = orchestrator.refine(request.feedback)

    return {
        "session_id": request.session_id,
        "iteration": context.iteration,
        "narrative": context.narrative,
        "musical_features": context.musical_features.to_dict(),
        "audio_file": context.audio_file,
        "pdf_file": context.pdf_file,
    }


@app.get("/status/{session_id}")
def status(session_id: str = "default"):
    """Get the current state of a pipeline session."""
    orchestrator = sessions.get(session_id)
    if not orchestrator:
        return {"error": f"No active session '{session_id}'."}
    return orchestrator.get_status()
