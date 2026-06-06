import json

from pydantic import BaseModel, field_validator


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict

    @field_validator("arguments", mode="before")
    @classmethod
    def parse_arguments(cls, value):
        # Vapi può inviare arguments come oggetto o come stringa JSON.
        if isinstance(value, str):
            return json.loads(value)
        return value


class _Message(BaseModel):
    type: str
    toolCallList: list[ToolCall]


class ToolCallEnvelope(BaseModel):
    message: _Message
