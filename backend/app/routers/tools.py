from fastapi import APIRouter, Depends

from backend.app.config import settings
from backend.app.deps import get_repo
from backend.app.models.vapi import ToolCallEnvelope
from backend.app.services.appointments import booking
from backend.app.services.appointments.repository import AppointmentRepository
from backend.app.vapi_adapter import handle_envelope

router = APIRouter(prefix="/tools")


@router.post("/disponibilita")
def disponibilita(envelope: ToolCallEnvelope, repo: AppointmentRepository = Depends(get_repo)):
    return handle_envelope(
        envelope, lambda args: booking.disponibilita(repo, args, settings.slot_hours)
    )


@router.post("/crea_appuntamento")
def crea_appuntamento(envelope: ToolCallEnvelope, repo: AppointmentRepository = Depends(get_repo)):
    return handle_envelope(
        envelope, lambda args: booking.crea_appuntamento(repo, args, settings.slot_hours)
    )
