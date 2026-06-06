# Roadmap & stato

Sviluppo per fasi. Le prime portano a un sistema funzionante end-to-end; le successive aggiungono
qualità e contorno. Per il *come* è progettato il sistema vedi [BLUEPRINT.md](BLUEPRINT.md).

## Stato attuale (2026-06-06)

**Primo slice backend (prenotazione) implementato in TDD e su `main`.** 25 test verdi; smoke reale OK
(prenotazione → codice di conferma → stesso slot rifiutato → disponibilità aggiornata).

Implementato in `backend/app/`: FastAPI + `/health` · adapter contratto Vapi
(`toolCallList`↔`results[]`) · SQLite con `UNIQUE(servizio,data,ora)` anti doppia-prenotazione ·
service appuntamenti (`disponibilita` + `crea_appuntamento`, tutti gli edge case) · endpoint
`/tools/disponibilita` e `/tools/crea_appuntamento` · dependency injection del repository
(override-abile nei test). Ambiente: Python 3.11 (`.venv`).

> Slice **volutamente senza RAG** (`query_servizi`) e **senza wiring Vapi**, solo per ora: **non è la
> consegna finale.**

## Fasi

1. ✅ Impalcatura backend: FastAPI, configurazione, avvio locale.
2. ✅ Endpoint appuntamenti: verifica disponibilità e creazione, secondo il contratto dei tool.
3. ✅ Persistenza su SQLite, con controllo anti doppia prenotazione.
4. ⬜ Scraping del sito comunale e costruzione del corpus pulito.
5. ⬜ Recupero semantico (embedding multilingue + cosine in NumPy) ed endpoint `query_servizi`.
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

1. **Wiring Vapi** (config manuale, consuma crediti → mirato): `ngrok http 8000` → riallineare
   l'assistant al Comune (Deepgram `it`, GPT-4o, voce IT, system prompt) → collegare i 2 tool API
   Request agli endpoint `/tools/*` → test breve (chiedi slot, prenota, ritenta stesso slot) →
   export `vapi/assistant.json` (chiavi/ID rimossi).
2. **Slice RAG**: `query_servizi` con **fallback statico prima**, poi scraping crawl4ai → corpus →
   embedding → cosine NumPy. Qui si installano `sentence-transformers` + `numpy` (rinviati apposta).

## Riferimenti operativi

- **Repo GitHub:** https://github.com/Kieff90/Voicebot-PY (privata, branch `main`).
- **Account Vapi:** `vitamentepositiva@gmail.com` · PAYG ~10 crediti (~$10 ≈ 90 min).
  Assistant "Aria" id `e56a0784-f544-49da-92aa-41fdab8da7ff` — dominio "parrucchiere", da riallineare.
- **Avvio backend:** `uvicorn backend.app.main:app --reload --port 8000` (dopo `pip install -r
  requirements.txt -r requirements-dev.txt` nel venv).

## Test end-to-end (opzionale)

Se viene aggiunto un frontend, il flusso può essere verificato con uno strumento di automazione del
browser. Non è necessario al funzionamento del sistema.
