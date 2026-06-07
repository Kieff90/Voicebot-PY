from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_path: str = "data/appointments.db"
    slot_hours: list[str] = ["09:00", "10:00", "11:00", "12:00"]

    # RAG / recupero servizi — default = corpus reale (184 chunk, 25 servizi),
    # cosi chi clona la repo senza .env parte comunque con la base completa.
    # Per il corpus minimale di test/demo: RAG_CORPUS_PATH=data/fallback_services.jsonl
    rag_corpus_path: str = "data/services_cherasco.jsonl"
    rag_model_name: str = "intfloat/multilingual-e5-base"
    rag_top_k: int = 3
    # Tarata su corpus PULITO (184 chunk, dopo rimozione stub boilerplate) ed
    # eval set di 14 Q&A (8 in-dominio, 6 fuori). In-dominio reali: 0.855-0.896;
    # fuori-dominio: ≤0.840 (passaporto 0.838, carta d'identità 0.840, TARI 0.814).
    # 0.85 sta nel gap pulito (0.840 ↔ 0.855), favorendo la precisione: nessun
    # falso positivo. Resta fuori il solo "attività commerciale" (SUAP, 0.822):
    # mismatch di vocabolario ("produttive" vs "commerciale"), limite di recall.
    rag_threshold: float = 0.85
    rag_char_cap: int = 2000

    # Fallback quando l'informazione non e nel corpus: il backend fornisce i
    # contatti, Vapi formula la frase ("non ho questa informazione, contatta...").
    comune_telefono: str = "0172.427010"

    # Pannello admin (frontend minimale di sola lettura — protezione HTTP Basic).
    # Vuoti = pannello disabilitato (fail-closed): vedi backend/app/admin/auth.py.
    admin_user: str = ""
    admin_password: str = ""
    service_categories: list[str] = [
        "Anagrafe e stato civile",
        "Autorizzazioni",
        "Imprese e commercio",
        "Tributi, finanze e contravvenzioni",
        "Altro",
    ]


settings = Settings()
