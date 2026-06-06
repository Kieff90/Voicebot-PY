from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: str = "data/appointments.db"
    slot_hours: list[str] = ["09:00", "10:00", "11:00", "12:00"]


settings = Settings()
