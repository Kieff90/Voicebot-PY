import re
from datetime import date

from pydantic import BaseModel, field_validator

_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def _not_blank(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("valore vuoto")
    return value


class AvailabilityRequest(BaseModel):
    servizio: str
    data: str

    @field_validator("servizio")
    @classmethod
    def servizio_not_blank(cls, value: str) -> str:
        return _not_blank(value)

    @field_validator("data")
    @classmethod
    def data_is_iso(cls, value: str) -> str:
        date.fromisoformat(value)  # ValueError -> ValidationError
        return value


class AppointmentRequest(BaseModel):
    servizio: str
    data: str
    ora: str
    nome: str

    @field_validator("servizio")
    @classmethod
    def servizio_not_blank(cls, value: str) -> str:
        return _not_blank(value)

    @field_validator("nome")
    @classmethod
    def nome_not_blank(cls, value: str) -> str:
        return _not_blank(value)

    @field_validator("data")
    @classmethod
    def data_is_iso(cls, value: str) -> str:
        date.fromisoformat(value)
        return value

    @field_validator("ora")
    @classmethod
    def ora_is_hhmm(cls, value: str) -> str:
        if not _TIME_RE.match(value):
            raise ValueError("ora deve essere in formato HH:MM")
        return value
