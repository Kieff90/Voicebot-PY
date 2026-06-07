from fastapi import FastAPI

from backend.app.routers import admin, health, tools

app = FastAPI(title="CAI Voicebot Backend")
app.include_router(health.router)
app.include_router(tools.router)
app.include_router(admin.router)
