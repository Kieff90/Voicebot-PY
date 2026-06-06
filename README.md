# Voicebot servizi comunali — Comune di Codroipo

Assistente vocale in italiano che aiuta un cittadino a ottenere informazioni sui servizi del Comune
e a prenotare un appuntamento a uno sportello.

La parte vocale e conversazionale è gestita da Vapi. La conoscenza dei servizi e la logica degli
appuntamenti vivono in un backend FastAPI separato, che l'assistente interroga tramite tool durante
la chiamata.

## Come funziona

Il cittadino parla con l'assistente. Quando serve un dato reale, l'assistente chiama un endpoint del
backend (esposto in locale tramite ngrok); il backend risponde e l'assistente pronuncia il risultato.
La trascrizione, la sintesi vocale e la formulazione della risposta restano all'assistente; il
recupero delle informazioni e la gestione degli appuntamenti restano al backend.

Dettagli in [docs/BLUEPRINT.md](docs/BLUEPRINT.md) (design del sistema) e [docs/ROADMAP.md](docs/ROADMAP.md) (fasi e stato).

## Stack

- Vapi: trascrizione (Deepgram), modello linguistico (GPT-4o), voce italiana
- Python, FastAPI
- Recupero semantico: sentence-transformers + cosine in NumPy (FAISS come upgrade se il corpus cresce)
- Appuntamenti: SQLite
- Acquisizione contenuti del sito comunale: crawl4ai (offline)
- Esposizione locale: ngrok

## Requisiti

- Python 3.11+
- Un account Vapi e la relativa chiave API
- ngrok

## Avvio

> I passi 3-5 valgono una volta implementato il backend (vedi [docs/ROADMAP.md](docs/ROADMAP.md), fase 1).
> Allo stato attuale `backend/` è ancora vuoto.

1. Creare un ambiente virtuale e installare le dipendenze:
   ```
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copiare `.env.example` in `.env` e inserire le proprie chiavi.
3. Avviare il backend:
   ```
   uvicorn backend.app.main:app --reload
   ```
4. Aprire il tunnel verso il backend:
   ```
   ngrok http 8000
   ```
5. Configurare i tool dell'assistente Vapi con l'URL ngrok (vedi [vapi/README.md](vapi/README.md)).

## Struttura

- `backend/` — API FastAPI: recupero informazioni e gestione appuntamenti
- `ingestion/` — acquisizione e indicizzazione dei contenuti del sito (offline)
- `vapi/` — configurazione dell'assistente da importare in Vapi
- `docs/` — `BLUEPRINT.md` (design del sistema), `ROADMAP.md` (fasi e stato), `architecture.html` (diagrammi apribili nel browser).

## Stato

Primo slice backend (prenotazione) implementato e testato. Dettaglio in [docs/ROADMAP.md](docs/ROADMAP.md);
progettazione in [docs/BLUEPRINT.md](docs/BLUEPRINT.md).
