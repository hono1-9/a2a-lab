# client/client.py

import httpx
import uuid
from typing import Any, Optional


class A2AClient:
    """Minimal A2A-compliant client."""

    def __init__(self, agent_url: str):
        self.agent_url = agent_url.rstrip("/")
        self._card = None       # cached Agent Card
        self._http = httpx.Client(timeout=30)

    # ── Context Manager ───────────────────────────────────────────────
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    # ── 1. Discovery ──────────────────────────────────────────────────
    def fetch_agent_card(self) -> dict:
        """Fetch and cache the Agent Card."""
        if self._card is None:
            url = f"{self.agent_url}/.well-known/agent.json"
            resp = self._http.get(url)
            resp.raise_for_status()
            self._card = resp.json()
        return self._card

    def get_skills(self) -> list:
        """Return the skills list from the cached Agent Card."""
        card = self.fetch_agent_card()
        return card.get("skills", [])

    # ── 2. Request Construction ───────────────────────────────────────
    def _build_task(
        self,
        text: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> dict:
        """Build a conformant A2A task payload."""
        return {
            "id":        task_id or str(uuid.uuid4()),
            "sessionId": session_id,
            "message": {
                "role":  "user",
                "parts": [{"type": "text", "text": text}],
            },
        }

    # ── 3. Send & Parse ───────────────────────────────────────────────
    def send_task(self, text: str, **kwargs) -> dict:
        """Send a task and return the parsed response."""
        self.fetch_agent_card()   # ensure card is cached
        payload = self._build_task(text, **kwargs)
        url = f"{self.agent_url}/tasks/send"
        resp = self._http.post(url, json=payload)
        resp.raise_for_status()
        response = resp.json()

        # Check response status
        state = response.get("status", {}).get("state")
        if state != "completed":
            raise RuntimeError(
                f"Task did not complete successfully. "
                f"status.state='{state}'. Full response: {response}"
            )

        return response

    # ── 4. Helper: extract result text ────────────────────────────────
    @staticmethod
    def extract_text(response: dict) -> str:
        """Pull the first text or file url from artifacts."""
        artifacts = response.get("artifacts", [])
        for artifact in artifacts:
            for part in artifact.get("parts", []):
                if part.get("type") == "text":
                    return part["text"]
                if part.get("type") == "file":
                    return part.get("file", {}).get("url", "")
        return ""

    # ── 5. Cleanup ────────────────────────────────────────────────────
    def close(self):
        """Close the underlying HTTP client."""
        self._http.close()