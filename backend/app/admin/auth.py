import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from backend.app.config import settings

_security = HTTPBasic()


def require_admin(credentials: HTTPBasicCredentials = Depends(_security)) -> None:
    """Dependency FastAPI: protegge una rotta con HTTP Basic da .env.

    Fail-closed: se le credenziali non sono configurate il pannello resta
    chiuso (503), per evitare il bypass con credenziali vuote quando il
    backend è esposto pubblicamente via ngrok.
    """
    if not settings.admin_user or not settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pannello admin non configurato",
        )
    user_ok = secrets.compare_digest(credentials.username, settings.admin_user)
    password_ok = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (user_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Basic"},
        )
