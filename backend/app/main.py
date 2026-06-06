from fastapi import FastAPI

from backend.app.routers import health

app = FastAPI(title="CAI Voicebot Backend")
app.include_router(health.router)
