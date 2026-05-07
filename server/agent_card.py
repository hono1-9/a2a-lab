# server/agent_card.py

AGENT_CARD = {
    "id":          "echo-agent-v1",
    "name":        "Echo Agent",
    "version":     "1.0.0",
    "description": "A simple agent that echoes back any text it receives.",
    "url": "https://echo-a2a-agent-525803800713.us-central1.run.app",
    "capabilities": {
        "streaming":         False,
        "pushNotifications": False
    },
    "defaultInputModes":  ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "contact": {
        "email": "agent@example.com"
    },
    "skills": [
        {
            "id":          "echo",
            "name":        "Echo",
            "description": "Returns the user message verbatim.",
            "inputModes":  ["text/plain"],
            "outputModes": ["text/plain"]
        },
        {
            "id":          "summarise",
            "name":        "Summarise",
            "description": "Returns a one-sentence summary of the provided text.",
            "inputModes":  ["text/plain"],
            "outputModes": ["text/plain"]
        }
    ]
}


def validate_card(card: dict) -> bool:
    """
    Validate that an Agent Card dictionary contains all required top-level fields.

    Required fields: id, name, version, description, url, capabilities,
    defaultInputModes, defaultOutputModes, skills.

    Returns True if all required fields are present, False otherwise.
    """
    required_fields = [
        "id",
        "name",
        "version",
        "description",
        "url",
        "capabilities",
        "defaultInputModes",
        "defaultOutputModes",
        "skills",
    ]
    for field in required_fields:
        if field not in card:
            return False
    return True