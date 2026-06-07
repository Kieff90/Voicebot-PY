# Frontend minimale prenotazioni — design

Data: 2026-06-07
Stato: approvato, pronto per il piano di implementazione

## Obiettivo

Coprire l'elemento aggiuntivo richiesto dal test ("piccolo frontend per visualizzare
gli appuntamenti prenotati") con una pagina web minimale, di sola lettura, che mostra
in tabella gli appuntamenti gia salvati su SQLite, con filtri per intervallo di date e
per categoria di servizio.

L'altro elemento aggiuntivo del test (persistenza su database invece che in memoria) e
gia soddisfatto dal primo slice: gli appuntamenti vivono in SQLite fin dall'inizio.
Questo va dichiarato nella nota scelte/limiti, non richiede sviluppo.

## Scope

Incluso:

- Pagina HTML server-side con la tabella degli appuntamenti.
- Filtri: intervallo temporale (dal giorno al giorno, estremi inclusi) e categoria
  servizio (menu a tendina, lista fissa).
- Protezione con HTTP Basic, credenziali da variabile d'ambiente.

Escluso (YAGNI):

- Log delle conversazioni: oggi non sono salvati nel backend (vivono nella dashboard
  Vapi); mostrarli richiederebbe un layer nuovo (webhook + tabella + ingest). Fuori scope.
- Modifica o cancellazione appuntamenti: la pagina e di sola lettura.
- Paginazione, ordinamento lato client, framework JavaScript, build step.

## Architettura

Tutto dentro il backend FastAPI esistente. Nessuna applicazione separata.

Flusso dati:

```
Browser -> GET /admin/appointments?data_da=...&data_a=...&servizio=...  (HTTP Basic)
        -> dependency require_admin valida user/password da .env
        -> repo.list_all(data_da, data_a, servizio)  (SELECT con WHERE dinamico)
        -> Jinja2 renderizza la tabella + ripopola la form
        -> HTML
```

Il form e di tipo GET: i filtri finiscono in query string, quindi l'URL e
condivisibile e lo stato della form viene mantenuto al reload.

## Componenti

### 1. Repository (backend/app/services/appointments/repository.py)

Due metodi nuovi, nessuna business rule (coerente con il pattern esistente):

- `list_all(data_da=None, data_a=None, servizio=None) -> list[sqlite3.Row]`
  Query parametrizzata con WHERE costruito dinamicamente dai filtri presenti.
  Le date sono ISO `YYYY-MM-DD`: il confronto `>=` / `<=` funziona in ordine
  lessicografico, senza parsing. Ordinamento `ORDER BY data, ora`.
  Colonne selezionate: codice, servizio, data, ora, nome, stato.

- (eventuale) nessun metodo extra per le categorie: la lista e fissa, vedi sotto.

### 2. Categorie servizio (backend/app/config.py)

Costante nelle impostazioni, lista fissa (niente valori sparsi nel codice):

```
service_categories = [
    "Anagrafe e stato civile",
    "Autorizzazioni",
    "Imprese e commercio",
    "Tributi, finanze e contravvenzioni",
    "Altro",
]
```

Queste voci corrispondono ai valori realmente salvati nel campo `servizio` degli
appuntamenti (il flusso di prenotazione salva la macro-categoria), quindi il filtro
fa match esatto senza mappature.

### 3. Autenticazione (backend/app/admin/auth.py)

Dependency `require_admin` con `HTTPBasic` di FastAPI. Confronto con
`secrets.compare_digest` contro `settings.admin_user` e `settings.admin_password`.
Mismatch o credenziali assenti -> `401` con header `WWW-Authenticate: Basic`.

Su ngrok il canale e HTTPS, quindi le credenziali viaggiano cifrate. La protezione
serve a non esporre i dati personali (nomi dei cittadini) sull'URL pubblico ngrok.

Config (backend/app/config.py) + .env.example: due campi nuovi, `admin_user` e
`admin_password`, senza default in chiaro (vuoti, da valorizzare nel .env).

### 4. Router (backend/app/routers/admin.py)

Rotta `GET /admin/appointments`, dipende da `require_admin` e `get_repo`.
Legge i tre query param opzionali (`data_da`, `data_a`, `servizio`), li passa al repo
e li ripassa al template per ripopolare la form.

Validazione al confine: se una data non e ISO valida, quel filtro viene ignorato e la
pagina non va in errore.

### 5. Template (backend/app/templates/appointments.html)

- Titolo (`<title>` e `<h1>`): "Prenotazioni Servizi — Comune di Cherasco".
- Barra filtri in alto: due input `type="date"` (Dal / Al), un `<select>` servizio
  con prima voce "Tutti" piu le 5 categorie, pulsante "Filtra", link "Azzera".
  Il `<select>` mostra come selezionata la categoria corrente.
- Tabella con colonne: data, ora, servizio, nome, codice, stato.
  (`created_at` resta nel DB ma non in tabella.)
- Stato vuoto: "Nessun appuntamento prenotato".
- CSS inline essenziale, niente JavaScript.

### 6. Wiring

- `Jinja2Templates(directory="backend/app/templates")`.
- `main.py` include `admin.router`.
- `jinja2` aggiunto a `requirements.txt`.

## Test (TDD, prima il test)

Repository (tests/test_repository.py):

- `list_all` senza filtri ritorna tutte le righe ordinate per data, ora.
- `list_all` con intervallo di date filtra correttamente (esclude fuori range).
- `list_all` con `servizio` filtra per categoria.
- filtri combinati (date + servizio).

Admin (tests/test_admin.py, nuovo):

- `401` senza credenziali.
- `200` con credenziali corrette.
- la pagina contiene il nome di un appuntamento creato.
- `?servizio=...` mostra solo le righe di quella categoria.
- intervallo di date esclude le righe fuori range.
- data malformata non rompe la pagina (filtro ignorato).
- stato vuoto quando non ci sono appuntamenti.

Fixture: DB in memoria (come i test esistenti), `monkeypatch` su
`settings.admin_user` / `settings.admin_password`, `TestClient(..., auth=(...))`.

## Documentazione

Aggiungere a docs/NOTA_SCELTE_LIMITI.md una riga: la persistenza su database (secondo
elemento aggiuntivo del test) era gia implementata fin dal primo slice del backend.
