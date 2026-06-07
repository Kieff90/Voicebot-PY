from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from backend.app.admin.auth import require_admin
from backend.app.config import settings
from backend.app.deps import get_repo
from backend.app.services.appointments.repository import AppointmentRepository

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])

_templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def _validated_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        date.fromisoformat(value)
    except ValueError:
        return None
    return value


@router.get("/appointments")
def appointments(
    request: Request,
    data_da: str | None = None,
    data_a: str | None = None,
    servizio: str | None = None,
    repo: AppointmentRepository = Depends(get_repo),
):
    data_da = _validated_date(data_da)
    data_a = _validated_date(data_a)
    if data_da and data_a and data_a < data_da:
        data_a = None
    servizio = servizio if servizio in settings.service_categories else None

    righe = repo.list_all(data_da=data_da, data_a=data_a, servizio=servizio)
    return _templates.TemplateResponse(
        request,
        "appointments.html",
        {
            "appuntamenti": righe,
            "categorie": settings.service_categories,
            "data_da": data_da or "",
            "data_a": data_a or "",
            "servizio": servizio or "",
        },
    )
