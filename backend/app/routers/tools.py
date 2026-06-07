from fastapi import APIRouter, Depends

from backend.app.config import settings
from backend.app.deps import get_rag, get_repo
from backend.app.services.appointments import booking
from backend.app.services.appointments.repository import AppointmentRepository
from backend.app.services.rag import retriever

router = APIRouter(prefix="/tools")

# I tool Vapi sono di tipo "API Request": inviano i soli parametri estratti
# (es. {"domanda": "..."}) e ricevono il risultato grezzo. La validazione al
# confine e la gestione degli errori (esito: errore/non_disponibile) avvengono
# nei service, che restituiscono un dict pronto da leggere per il modello.


@router.post("/disponibilita")
def disponibilita(payload: dict, repo: AppointmentRepository = Depends(get_repo)):
    return booking.disponibilita(repo, payload, settings.slot_hours)


@router.post("/crea_appuntamento")
def crea_appuntamento(payload: dict, repo: AppointmentRepository = Depends(get_repo)):
    return booking.crea_appuntamento(repo, payload, settings.slot_hours)


@router.post("/query_servizi")
def query_servizi(payload: dict, rag=Depends(get_rag)):
    index, embedder = rag
    return retriever.query_servizi(
        index,
        embedder,
        payload,
        top_k=settings.rag_top_k,
        threshold=settings.rag_threshold,
        char_cap=settings.rag_char_cap,
        telefono=settings.comune_telefono,
    )
