# Nota — scelte, limiti, migliorie, strumenti AI

Nota breve richiesta dai criteri di consegna del test. Per il dettaglio architetturale vedi
[BLUEPRINT.md](BLUEPRINT.md).

## Scelte effettuate

- Logica nel backend, non in Vapi: mantiene RAG, regole di prenotazione e persistenza testabili in
  isolamento e indipendenti dal vendor vocale.
- Tre tool atomici (`query_servizi`, `disponibilita`, `crea_appuntamento`, uno per responsabilità):
  l'LLM li sceglie con più precisione e gli edge case restano isolati.
- Recupero senza secondo LLM: il backend fa solo retrieval (cosine NumPy su embedding locali), la
  generazione resta in Vapi (GPT-4.1).
- Indice in memoria con cosine NumPy invece di FAISS o vector DB esterni: per 184 chunk uno scan
  lineare è preciso e più semplice da gestire; FAISS resta documentato come evoluzione possibile se
  il corpus crescesse molto.
- SQLite con vincolo `UNIQUE(servizio, data, ora)`: la garanzia anti doppia-prenotazione sta nel
  database, non nel codice applicativo.
- Validazione Pydantic al confine: l'input che arriva dall'LLM non è affidabile, può mancare o
  avere un formato inatteso.
- Fallback statico per il corpus: la demo non dipende dalla riuscita live di scraping e
  indicizzazione.

## Limitazioni

- L'esposizione del backend passa da ngrok: si usa un dominio statico (non cambia ai riavvii) ma
  resta un'esposizione locale, non un deploy stabile.
- L'acquisizione dei contenuti dipende dalla struttura del sito comunale: un cambiamento al sito
  richiede di rivedere lo scraper.
- La soglia di recupero (0.85) privilegia la precisione: domande su servizi assenti dal sito di
  Cherasco (carta d'identità, passaporto, TARI, CIE) cadono nel fallback contatti perché quei
  servizi non sono schede sul sito, non per un errore di recupero.
- Mismatch lessicale noto: "aprire un'attività commerciale" arriva a 0.822, sotto soglia, perché il
  sito usa "attività produttive".
- Il budget del trial vocale è limitato: i test dal vivo sono stati mirati, non esaustivi.

## Cosa si migliorerebbe con più tempo

1. Espandere i chunk con sinonimi e varianti lessicali, per coprire mismatch come "attività
   commerciale" / "attività produttive".
2. Sostituire ngrok con un hosting stabile del backend.
3. Ampliare l'eval set di retrieval oltre le attuali 14 domande.
4. Aggiungere un endpoint `verifica_appuntamento` per consultare una prenotazione esistente per
   codice (oggi `crea_appuntamento` copre solo la creazione).
5. Recupero ibrido (dense + BM25) per i match esatti su codici e nomi degli uffici, dove
   l'embedding semantico è meno preciso del confronto testuale.
6. Reranking con cross-encoder, utile soprattutto se il corpus crescesse molto oltre i 184 chunk
   attuali.

## Strumenti AI usati

- Claude (Anthropic), tramite Claude Code: progettazione del backend (architettura, contratto dei
  tool, modello dati), sviluppo in TDD, costruzione e taratura del corpus RAG (scraping, pulizia,
  soglia), scrittura e correzione del system prompt Vapi sulla base dei comportamenti osservati
  nelle chiamate reali, documentazione.
- crawl4ai + Playwright: acquisizione dei contenuti del sito comunale, necessaria per il rendering
  JavaScript del sito.
- sentence-transformers (`intfloat/multilingual-e5-base`): embedding multilingue per il recupero
  semantico, eseguito in locale; nessun contenuto del corpus viene inviato a servizi esterni a
  runtime.
- Vapi (GPT-4.1): generazione della risposta vocale a partire dai chunk recuperati dal backend;
  l'unico LLM generativo del sistema vive qui, non nel backend.
