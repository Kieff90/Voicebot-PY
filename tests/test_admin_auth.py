import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from backend.app.admin.auth import require_admin
from backend.app.config import settings


@pytest.fixture(autouse=True)
def admin_credentials(monkeypatch):
    monkeypatch.setattr(settings, "admin_user", "admin")
    monkeypatch.setattr(settings, "admin_password", "segreto")


def test_require_admin_accepts_correct_credentials():
    require_admin(HTTPBasicCredentials(username="admin", password="segreto"))


def test_require_admin_rejects_wrong_password():
    with pytest.raises(HTTPException) as exc_info:
        require_admin(HTTPBasicCredentials(username="admin", password="sbagliata"))
    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Basic"


def test_require_admin_rejects_wrong_username():
    with pytest.raises(HTTPException) as exc_info:
        require_admin(HTTPBasicCredentials(username="qualcun_altro", password="segreto"))
    assert exc_info.value.status_code == 401


def test_require_admin_fails_closed_when_not_configured(monkeypatch):
    # Senza credenziali configurate il pannello deve restare chiuso: niente
    # bypass con credenziali vuote (503, non 401).
    monkeypatch.setattr(settings, "admin_user", "")
    monkeypatch.setattr(settings, "admin_password", "")
    with pytest.raises(HTTPException) as exc_info:
        require_admin(HTTPBasicCredentials(username="", password=""))
    assert exc_info.value.status_code == 503
