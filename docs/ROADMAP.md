# Piano di sviluppo

Sviluppo per fasi. Le prime portano a un sistema funzionante da capo a fondo; le successive
aggiungono qualità e contorno.

## Fasi

1. Impalcatura del backend: FastAPI, configurazione, avvio locale.
2. Endpoint appuntamenti: verifica disponibilità e creazione, secondo il contratto dei tool.
3. Persistenza su SQLite, con controllo anti doppia prenotazione.
4. Scraping del sito comunale e costruzione del corpus pulito.
5. Recupero semantico (embedding multilingue + FAISS) ed endpoint di interrogazione dei servizi.
6. Collegamento dei tool all'assistente Vapi tramite ngrok.
7. Configurazione dell'assistente in italiano: trascrizione, voce, prompt di sistema.
8. Gestione dei casi limite nel prompt e nel backend.
9. Controlli di qualità e piccolo set di valutazione del recupero.
10. Contorno opzionale: containerizzazione, frontend, persistenza più strutturata.

## Percorso minimo (end-to-end)

Le fasi 1, 2, 3, 6 e 7 portano a una conversazione completa con prenotazione funzionante. Il recupero
delle informazioni (fasi 4 e 5) può partire da contenuti minimi e crescere. Il contorno (fase 10) è
incrementale, così esiste sempre una versione dimostrabile.

## Test end-to-end (opzionale)

Se viene aggiunto un frontend, il suo flusso può essere verificato con uno strumento di automazione
del browser. Non è necessario al funzionamento del sistema.
