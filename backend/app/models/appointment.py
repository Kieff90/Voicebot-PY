import re
from datetime import date

from pydantic import BaseModel, field_validator

_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


class AvailabilityRequest(BaseModel):
    servizio: str
    data: str

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
