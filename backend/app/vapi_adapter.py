from typing import Any, Callable

from backend.app.models.vapi import ToolCallEnvelope


def handle_envelope(
    envelope: ToolCallEnvelope, handler: Callable[[dict], Any]
) -> dict:
    """Unwrap toolCallList, esegue handler per ogni call, rewrap in results[]."""
    results = []
    for call in envelope.message.toolCallList:
        result = handler(call.arguments)
        results.append({"toolCallId": call.id, "result": result})
    return {"results": results}
