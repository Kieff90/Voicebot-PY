import pytest
from pydantic import ValidationError

from backend.app.models.appointment import AppointmentRequest, AvailabilityRequest


def test_availability_request_valid():
    req = AvailabilityRequest.model_validate({"servizio": "anagrafe", "data": "2026-12-01"})
    assert req.servizio == "anagrafe"
    assert req.data == "2026-12-01"


def test_availability_request_rejects_bad_date():
    with pytest.raises(ValidationError):
        AvailabilityRequest.model_validate({"servizio": "anagrafe", "data": "01/12/2026"})


def test_availability_request_rejects_blank_servizio():
    with pytest.raises(ValidationError):
        AvailabilityRequest.model_validate({"servizio": "   ", "data": "2026-12-01"})


def test_appointment_request_valid():
    req = AppointmentRequest.model_validate(
        {"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00", "nome": "Mario"}
    )
    assert req.ora == "09:00"


def test_appointment_request_rejects_missing_field():
    with pytest.raises(ValidationError):
        AppointmentRequest.model_validate({"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00"})


def test_appointment_request_rejects_bad_time():
    with pytest.raises(ValidationError):
        AppointmentRequest.model_validate(
            {"servizio": "anagrafe", "data": "2026-12-01", "ora": "9", "nome": "Mario"}
        )


def test_appointment_request_rejects_blank_servizio():
    with pytest.raises(ValidationError):
        AppointmentRequest.model_validate(
            {"servizio": "  ", "data": "2026-12-01", "ora": "09:00", "nome": "Mario"}
        )


def test_appointment_request_rejects_blank_nome():
    with pytest.raises(ValidationError):
        AppointmentRequest.model_validate(
            {"servizio": "anagrafe", "data": "2026-12-01", "ora": "09:00", "nome": "   "}
        )
