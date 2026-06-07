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
