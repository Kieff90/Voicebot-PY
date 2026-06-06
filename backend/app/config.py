from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: str = "data/appointments.db"
    slot_hours: list[str] = ["09:00", "10:00", "11:00", "12:00"]

    # RAG / recupero servizi
    rag_corpus_path: str = "data/fallback_services.jsonl"
    rag_model_name: str = "intfloat/multilingual-e5-base"
    rag_top_k: int = 3
    rag_threshold: float = 0.82  # provvisoria: tarata sull'eval set (vedi BLUEPRINT 7)
    rag_char_cap: int = 2000


settings = Settings()
