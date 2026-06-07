# Configurazione dell'assistente Vapi

Questa cartella contiene la configurazione dell'assistente vocale per i servizi del Comune di
Cherasco, da ricreare/importare su Vapi e da consegnare come parte del test.

## File

- `system_prompt.it.md` — prompt di sistema in italiano (6 sezioni, speech-optimized).
- `tools/query_servizi.json` — tool informazioni servizi → `POST /tools/query_servizi`.
- `tools/disponibilita.json` — tool verifica disponibilità → `POST /tools/disponibilita`.
- `tools/crea_appuntamento.json` — tool prenotazione → `POST /tools/crea_appuntamento`.
- `assistant.json` — export finale dell'assistante (aggiunto a fine wiring, con chiavi/ID rimossi).

## Parametri scelti

- **Modello:** GPT-4.1 (OpenAI).
- **Trascrizione:** Deepgram, `language: it` (non auto-detect: bot solo-italiano).
- **Voce:** voce italiana nativa Vapi (zero integration esterna, scelta per semplicità e budget).
- **Tre tool API Request** verso il backend FastAPI esposto via ngrok.

## Esposizione del backend (ngrok — dominio statico)

L'account ngrok usato in sviluppo ha un dominio statico gratuito: per **chi lo possiede**, l'URL non
cambia ai riavvii, quindi i tool si configurano una volta sola.

```bash
# 1. avvia il backend (venv con dipendenze installate)
uvicorn backend.app.main:app --reload --port 8000

# 2. esponi con il dominio statico
ngrok http 8000 --url=https://mummy-bronze-ferocious.ngrok-free.dev
```

Base URL dei tool in questo export: `https://mummy-bronze-ferocious.ngrok-free.dev`

> **Importante per chi clona la repo per testarla (es. valutazione CAI):** quel dominio è legato
> all'account ngrok dell'autore — eseguendo `ngrok http 8000` nel proprio ambiente si ottiene un
> **URL diverso**. Prima di avviare una chiamata di test, sostituire il Server URL nei 3 tool
> dell'assistente Vapi (sezione "Tools" nella dashboard, oppure nel JSON importato) con il proprio
> URL ngrok seguito dal path del tool, es. `https://<tuo-url>.ngrok-free.app/tools/query_servizi`.
> Senza questo passo i tool chiamano un backend non raggiungibile e l'assistente non avrà accesso
> a informazioni servizi/disponibilità/prenotazione.

## Contratto tool (riferimento)

Il contratto è JSON semplice: ogni tool riceve in POST il corpo con gli argomenti estratti dalla
conversazione (es. `{ "domanda": "..." }`) e il backend risponde con il risultato grezzo, senza
envelope. Argomenti e risultati reali:

| Tool | arguments | result (esiti possibili) |
|---|---|---|
| `query_servizi` | `{ domanda }` | `esito: ok` + `risultati[]` (servizio/sezione/testo/fonte) · `esito: non_disponibile` + `contatto` · `esito: errore` |
| `disponibilita` | `{ servizio, data }` | `slot_liberi[]` (orari 09:00–12:00 meno gli occupati) · `esito: pieno` se vuoto |
| `crea_appuntamento` | `{ servizio, data, ora, nome }` | `esito: confermato` + `codice` · `esito: errore` + `motivo` |

## Procedura passo-passo (dashboard Vapi)

Assistant: `Comune di Cherasco` (id `f3ea426c-c818-4c51-bdea-93bd5f938a5b`).

1. **Model**: provider OpenAI, modello GPT-4.1.
2. **Transcriber**: Deepgram, lingua Italiano (`it`).
3. **Voice**: voce italiana nativa Vapi.
4. **First message**: messaggio di benvenuto in italiano.
5. **System Prompt**: incolla il contenuto di `system_prompt.it.md`.
6. **Tools**: crea 3 tool "API Request" con i Server URL sopra (uno per endpoint) e collegali
   all'assistant. Nome/description/parametri come nei file `tools/*.json`.
7. **Test**: una web-call breve (consuma crediti) che copre domanda in-dominio, domanda
   fuori-dominio (fallback), prenotazione, doppia prenotazione.
8. **Export**: voce "More actions", poi "Configuration"; salva qui come `assistant.json`
   (rimuovendo chiavi e ID).

## Limiti noti

- Il backend gira in locale dietro ngrok: per una demo va avviato prima della chiamata.
- Gli slot appuntamento sono fissi (09:00, 10:00, 11:00, 12:00), configurabili via `slot_hours`.
