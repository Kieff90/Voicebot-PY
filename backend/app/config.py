from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: str = "data/appointments.db"
    slot_hours: list[str] = ["09:00", "10:00", "11:00", "12:00"]

    # RAG / recupero servizi
    rag_corpus_path: str = "data/fallback_services.jsonl"
    rag_model_name: str = "intfloat/multilingual-e5-base"
    rag_top_k: int = 3
    # Tarata su eval set 15 Q&A sul corpus reale (9 in-dominio, 6 fuori).
    # In-dominio corretti: 0.852-0.893; fuori-dominio: 0.793-0.818 (escluso CIE,
    # assente dal corpus → 0.856, gap di contenuto non risolvibile con la soglia).
    # 0.84 sta nel gap pulito (0.818 ↔ 0.852), favorendo la precisione.
    rag_threshold: float = 0.84
    rag_char_cap: int = 2000

    # Fallback quando l'informazione non e nel corpus: il backend fornisce i
    # contatti, Vapi formula la frase ("non ho questa informazione, contatta...").
    comune_telefono: str = "0172.427010"
    prenotazione_url: str = ""  # TODO: inserire link prenotazione appuntamento


settings = Settings()
