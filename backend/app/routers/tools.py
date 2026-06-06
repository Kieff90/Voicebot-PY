from fastapi import APIRouter, Depends

from backend.app.config import settings
from backend.app.deps import get_rag, get_repo
from backend.app.models.vapi import ToolCallEnvelope
from backend.app.services.appointments import booking
from backend.app.services.appointments.repository import AppointmentRepository
from backend.app.services.rag import retriever
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


@router.post("/query_servizi")
def query_servizi(envelope: ToolCallEnvelope, rag=Depends(get_rag)):
    index, embedder = rag
    return handle_envelope(
        envelope,
        lambda args: retriever.query_servizi(
            index,
            embedder,
            args,
            top_k=settings.rag_top_k,
            threshold=settings.rag_threshold,
            char_cap=settings.rag_char_cap,
            telefono=settings.comune_telefono,
            prenotazione_url=settings.prenotazione_url,
        ),
    )
