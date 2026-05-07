# server/handlers.py

async def handle_task(request) -> str:
    """
    Process an A2A task request and return a result string.

    Supports the following skills:
    - !summarise <text>: Returns a one-sentence mock summary.
    - (default): Echoes the combined input text back unchanged.
    """
    text_parts = [p.text for p in request.message.parts if p.type == "text"]
    combined = " ".join(text_parts)

    # !summarise skill: return a fixed one-sentence mock summary
    if combined.startswith("!summarise"):
        return "This is a one-sentence mock summary of the provided text."

    # ECHO skill: return the input unchanged
    return combined