# server/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Optional
import uuid, datetime

from agent_card import AGENT_CARD
from handlers import handle_task

app = FastAPI(title="Echo A2A Agent")


# ── Endpoint 1: Agent Card ────────────────────────────────────────────
@app.get("/.well-known/agent.json")
async def get_agent_card():
    return AGENT_CARD


# ── Endpoint 2: Health Check ──────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "agent": AGENT_CARD["id"]}


# ── Pydantic models for the A2A task message schema ───────────────────
class TextPart(BaseModel):
    type: str = "text"
    text: str


class FileContent(BaseModel):
    url: str
    mimeType: str


class FilePart(BaseModel):
    type: str = "file"
    file: FileContent


class Message(BaseModel):
    role: str           # 'user' or 'agent'
    parts: list[TextPart | FilePart]


class TaskRequest(BaseModel):
    id: str             # client-generated task ID
    sessionId: Optional[str] = None
    message: Message
    metadata: Optional[dict[str, Any]] = None


# ── Endpoint 3: Send Task ─────────────────────────────────────────────
@app.post("/tasks/send")
async def send_task(request: TaskRequest):
    # Error handling: reject empty parts
    if not request.message.parts:
        raise HTTPException(status_code=400, detail="message.parts must not be empty")

    result_text = await handle_task(request)
    return {
        "id":     request.id,
        "status": {"state": "completed"},
        "artifacts": [
            {
                "parts": [{"type": "text", "text": result_text}]
            }
        ]
    }