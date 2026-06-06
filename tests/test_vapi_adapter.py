import json

import pytest
from pydantic import ValidationError

from backend.app.models.vapi import ToolCallEnvelope
from backend.app.vapi_adapter import handle_envelope


def _envelope(name="disponibilita", arguments=None, call_id="call_1"):
    return {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {"id": call_id, "name": name, "arguments": arguments or {"servizio": "anagrafe"}}
            ],
        }
    }


def test_parses_arguments_as_dict():
    env = ToolCallEnvelope.model_validate(_envelope(arguments={"servizio": "anagrafe"}))
    assert env.message.toolCallList[0].arguments == {"servizio": "anagrafe"}


def test_parses_arguments_when_json_string():
    payload = _envelope(arguments={"servizio": "anagrafe"})
    payload["message"]["toolCallList"][0]["arguments"] = json.dumps({"servizio": "anagrafe"})
    env = ToolCallEnvelope.model_validate(payload)
    assert env.message.toolCallList[0].arguments == {"servizio": "anagrafe"}


def test_rejects_envelope_without_toolcalllist():
    with pytest.raises(ValidationError):
        ToolCallEnvelope.model_validate({"message": {"type": "tool-calls"}})


def test_handle_envelope_rewraps_result_with_same_id():
    env = ToolCallEnvelope.model_validate(_envelope(call_id="abc"))
    out = handle_envelope(env, lambda args: {"echo": args["servizio"]})
    assert out == {"results": [{"toolCallId": "abc", "result": {"echo": "anagrafe"}}]}
