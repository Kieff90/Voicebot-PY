import secrets
import sqlite3
from datetime import date, datetime

from pydantic import ValidationError

from backend.app.models.appointment import AppointmentRequest, AvailabilityRequest
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


def crea_appuntamento(
    repo: AppointmentRepository,
    arguments: dict,
    slot_hours: list[str],
    *,
    now: datetime | None = None,
) -> dict:
    try:
        req = AppointmentRequest.model_validate(arguments)
    except ValidationError:
        return _errore("dati incompleti o non validi")

    if req.ora not in slot_hours:
        return _errore("orario non disponibile")

    now = now or datetime.now()
    data_richiesta = date.fromisoformat(req.data)
    if data_richiesta < now.date():
        return _errore("data nel passato")
    if data_richiesta == now.date() and req.ora < now.strftime("%H:%M"):
        return _errore("data nel passato")
    if req.ora in repo.booked_slots(req.servizio, req.data):
        return _errore("slot non disponibile")

    codice = secrets.token_hex(4).upper()
    try:
        repo.create(
            codice=codice,
            servizio=req.servizio,
            data=req.data,
            ora=req.ora,
            nome=req.nome,
        )
    except sqlite3.IntegrityError:
        # rete di sicurezza anti-race: lo slot è stato preso nel frattempo
        return _errore("slot non disponibile")

    return {
        "esito": "confermato",
        "codice": codice,
        "servizio": req.servizio,
        "data": req.data,
        "ora": req.ora,
    }
