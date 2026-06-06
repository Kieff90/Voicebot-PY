# Note di progettazione

Scelte principali, limiti noti e possibili miglioramenti.

## Perché il backend è separato dall'assistente

L'assistente Vapi gestisce voce e conversazione e ha già un modello linguistico attivo durante la
chiamata. Tenere la conoscenza dei servizi e le regole degli appuntamenti in un backend a parte dà
tre vantaggi: la logica si testa senza passare dalla voce, i dati persistono oltre la singola
chiamata, e il sistema non dipende dai dettagli di una specifica piattaforma vocale.

Il backend funziona come retriever. Per le domande sui servizi restituisce i passaggi di testo più
pertinenti, e la formulazione della risposta resta all'assistente. In questo modo si evita una
seconda chiamata a un modello generativo, con un risparmio di latenza e di costo.

## Recupero delle informazioni

I contenuti del sito comunale vengono acquisiti una volta, divisi in blocchi di circa 300 token con
una sovrapposizione del 10 per cento, e trasformati in vettori con un modello di embedding multilingue
(`multilingual-e5-base`). A ogni domanda la domanda viene vettorizzata e si recuperano i blocchi più
vicini per similarità del coseno, restituendone al massimo tre.

Per la quantità di contenuti di un Comune (un centinaio di blocchi) il confronto avviene in memoria con
NumPy: una scansione lineare è esatta, istantanea e si legge in poche righe, senza dipendenze
aggiuntive. Un indice FAISS resta come possibile evoluzione quando il corpus cresce, non come scelta di
partenza. Il modello multilingue è invece legato alla lingua della conversazione.

Per proteggere la demo, accanto al corpus acquisito è previsto un piccolo insieme di servizi curato a
mano (`fallback_services.jsonl`): se lo scraping o l'indice non sono disponibili al momento della
chiamata, l'assistente risponde comunque sui servizi principali.

Il modello `multilingual-e5-base` richiede una convenzione precisa: le domande vanno prefissate con
`query:` e i testi indicizzati con `passage:`, e i vettori vanno normalizzati prima del confronto per
similarità. Senza questi accorgimenti la qualità del recupero cala.

Per le risposte, il prompt dell'assistente impone di basarsi solo sui passaggi recuperati e di
dichiarare quando un'informazione non è disponibile, invece di inventarla.

## Appuntamenti

Gli appuntamenti sono salvati in SQLite. La verifica della disponibilità e la creazione passano da un
controllo che impedisce la doppia prenotazione dello stesso slot.

## Limiti noti

- Il tunnel ngrok cambia indirizzo a ogni riavvio, quindi l'URL configurato nei tool va aggiornato.
- L'acquisizione dei contenuti dipende dalla struttura del sito comunale e va rivista se il sito cambia.
- Il budget del free trial della piattaforma vocale è limitato, perciò i test vanno mirati.

## Possibili miglioramenti con più tempo

- Un riordino dei risultati (reranking) con un cross-encoder, utile su una base di conoscenza più ampia.
- Recupero ibrido, semantico più parole chiave, per i termini esatti come nomi di uffici o codici.
- Un deploy stabile del backend, per non dipendere da ngrok durante le dimostrazioni.
- Un piccolo insieme di domande e risposte di riferimento per misurare la qualità del recupero.

## Strumenti di AI usati

Lo sviluppo è stato assistito da Claude (Anthropic) per la progettazione e la documentazione. Gli
embedding usano modelli open-source della famiglia sentence-transformers. In esecuzione il backend
non invia i contenuti a servizi esterni: il recupero avviene in locale.
