# Voicebot servizi comunali — Comune di Cherasco

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

Oltre agli endpoint vocali, il backend espone un pannello web di sola lettura
(`/admin/appointments`) per consultare gli appuntamenti prenotati, con filtri per intervallo di date
e categoria di servizio. È una pagina HTML generata lato server (protetta da HTTP Basic via
`ADMIN_USER`/`ADMIN_PASSWORD`, disabilitata di default — vedi `.env.example`) e senza JavaScript di
build, pensata per uno sportello che vuole vedere a colpo d'occhio le prenotazioni registrate.

Dettagli in [docs/BLUEPRINT.md](docs/BLUEPRINT.md) (design del sistema).

## Stack

- Vapi: trascrizione (Deepgram), modello linguistico (GPT-4.1), voce italiana
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
   Il pannello prenotazioni è poi visibile su `http://127.0.0.1:8000/admin/appointments`.
4. Aprire il tunnel verso il backend:
   ```
   ngrok http 8000
   ```
5. Configurare i tool dell'assistente Vapi con l'URL ngrok (vedi [vapi/README.md](vapi/README.md)).

## Struttura

- `backend/` — API FastAPI: recupero informazioni, gestione appuntamenti e pannello web prenotazioni
- `ingestion/` — acquisizione e indicizzazione dei contenuti del sito (offline)
- `vapi/` — configurazione dell'assistente da importare in Vapi
- `docs/` — `BLUEPRINT.md` (design del sistema), `NOTA_SCELTE_LIMITI.md` (scelte, limiti, migliorie), `architecture.html` (diagrammi apribili nel browser).

## Stato

Backend di prenotazione, RAG e pannello web di consultazione appuntamenti implementati e testati.
Progettazione in [docs/BLUEPRINT.md](docs/BLUEPRINT.md).
