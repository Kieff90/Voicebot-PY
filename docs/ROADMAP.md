# Roadmap & stato

Sviluppo per fasi. Le prime portano a un sistema funzionante end-to-end; le successive aggiungono
qualità e contorno. Per il *come* è progettato il sistema vedi [BLUEPRINT.md](BLUEPRINT.md).

## Stato attuale (2026-06-06)

**Slice backend prenotazione + RAG corpus statico implementati in TDD e su `main`.** 46 test verdi.

Slice prenotazione: FastAPI + `/health` · adapter contratto Vapi (`toolCallList`↔`results[]`) ·
SQLite `UNIQUE(servizio,data,ora)` anti doppia-prenotazione · service appuntamenti · endpoint
`/tools/disponibilita` e `/tools/crea_appuntamento` · dependency injection del repository.

Slice RAG corpus statico: endpoint `/tools/query_servizi` · `Chunk` immutabile con metadati
(servizio/sezione/fonte/aggiornato) · `embed_text()` con prefisso disambiguante · indice cosine
NumPy · gate soglia · cap caratteri · `FakeEmbedder` deterministico per i test · corpus
`data/fallback_services.jsonl` (servizi reali SUAP Cherasco, 8 sezioni). Ambiente: Python 3.11.

> Senza scraping completo (26 servizi Cherasco) e senza wiring Vapi: **non è la consegna finale.**

## Fasi

1. ✅ Impalcatura backend: FastAPI, configurazione, avvio locale.
2. ✅ Endpoint appuntamenti: verifica disponibilità e creazione, secondo il contratto dei tool.
3. ✅ Persistenza su SQLite, con controllo anti doppia prenotazione.
4. ⬜ Scraping del sito comunale e costruzione del corpus completo (26 servizi Cherasco).
5. ✅ Recupero semantico (embedding multilingue + cosine in NumPy) ed endpoint `query_servizi` — corpus statico ok, scraping da completare.
6. ⬜ Collegamento dei tool all'assistente Vapi tramite ngrok.
7. ⬜ Configurazione dell'assistente in italiano: trascrizione, voce, prompt di sistema.
8. ⬜ Gestione dei casi limite nel prompt e nel backend.
9. ⬜ Controlli di qualità e piccolo set di valutazione del recupero.
10. ⬜ Contorno opzionale: containerizzazione, frontend, persistenza più strutturata.

## Percorso minimo (end-to-end)

Le fasi 1, 2, 3, 6 e 7 portano a una conversazione completa con prenotazione funzionante (fasi 1-3
fatte). Il recupero informazioni (4-5) può partire da contenuti minimi (fallback statico) e crescere.
Il contorno (10) è incrementale: esiste sempre una versione dimostrabile.

## Prossimi step concreti

1. **Scraping Cherasco** (crawl4ai, offline): script `ingestion/scraper_cherasco.py` → lista 26 URL
   servizi → corpus `data/services_cherasco.jsonl` → rebuild index con E5 reale → taratura soglia
   (mini eval 8-10 Q&A, misura score cosine reali, scegli cut-off con evidenza).
2. **Wiring Vapi** (config manuale, consuma crediti → mirato): `ngrok http 8000` → riallineare
   l'assistant al Comune Cherasco (Deepgram `it`, GPT-4o, voce IT, system prompt) → collegare i 3
   tool API Request agli endpoint `/tools/*` → test breve → export `vapi/assistant.json`.

## Riferimenti operativi

- **Repo GitHub:** https://github.com/Kieff90/Voicebot-PY (privata, branch `main`).
- **Account Vapi:** `vitamentepositiva@gmail.com` · PAYG ~10 crediti (~$10 ≈ 90 min).
  Assistant "Aria" id `e56a0784-f544-49da-92aa-41fdab8da7ff` — dominio "parrucchiere", da riallineare.
- **Avvio backend:** `uvicorn backend.app.main:app --reload --port 8000` (dopo `pip install -r
  requirements.txt -r requirements-dev.txt` nel venv).

## Test end-to-end (opzionale)

Se viene aggiunto un frontend, il flusso può essere verificato con uno strumento di automazione del
browser. Non è necessario al funzionamento del sistema.
