# server/agent_engine_wrapper.py
import uuid
from agent_card import AGENT_CARD
from handlers import handle_task


class EchoAgent:
    """Agent Engine wrapper for the Echo A2A Agent."""

    def set_up(self):
        # Called once when the container starts.
        # Initialise models, DB connections, etc. here.
        print('EchoAgent.set_up() called')

    def query(self, *, task_id: str = None, message_text: str) -> dict:
        """
        Agent Engine calls this method for each request.
        We mirror the A2A task send/receive pattern here.
        """
        from types import SimpleNamespace

        # Re-use the same handler logic as the HTTP server
        fake_request = SimpleNamespace(
            id=task_id or str(uuid.uuid4()),
            message=SimpleNamespace(
                role='user',
                parts=[SimpleNamespace(type='text', text=message_text)]
            )
        )

        import asyncio
        result_text = asyncio.run(handle_task(fake_request))

        return {
            'id':        fake_request.id,
            'status':    {'state': 'completed'},
            'artifacts': [{'parts': [{'type': 'text', 'text': result_text}]}]
        }