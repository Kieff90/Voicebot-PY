from pydantic import ValidationError

from backend.app.models.appointment import AvailabilityRequest
from backend.app.services.appointments.repository import AppointmentRepository


def _errore(motivo: str) -> dict:
    return {"esito": "errore", "motivo": motivo}


def disponibilita(
    repo: AppointmentRepository, arguments: dict, slot_hours: list[str]
) -> dict:
    try:
        req = AvailabilityRequest.model_validate(arguments)
    except ValidationError:
        return _errore("dati non validi")

    occupati = repo.booked_slots(req.servizio, req.data)
    liberi = [ora for ora in slot_hours if ora not in occupati]
    result = {"servizio": req.servizio, "data": req.data, "slot_liberi": liberi}
    if not liberi:
        result["esito"] = "pieno"
    return result
