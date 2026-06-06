"""Validazione al confine per il tool query_servizi."""

from pydantic import BaseModel, field_validator


class QueryRequest(BaseModel):
    domanda: str

    @field_validator("domanda")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("domanda vuota")
        return value
