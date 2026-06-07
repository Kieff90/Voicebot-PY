# Frontend minimale prenotazioni — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere una pagina `GET /admin/appointments` (sola lettura, protetta con HTTP Basic) che mostra in tabella gli appuntamenti già salvati su SQLite, con filtri per intervallo di date e per categoria di servizio.

**Architecture:** Tutto dentro il backend FastAPI esistente: un nuovo metodo di lettura sul repository esistente, una dependency di autenticazione, un router Jinja2 server-side, un template HTML senza JavaScript. Nessuna app separata, nessuna nuova tabella.

**Tech Stack:** FastAPI, Jinja2 (server-side templates), SQLite (`sqlite3`), pytest + `TestClient`.

---

## Mappa dei file

- Modifica: `backend/app/services/appointments/repository.py` — nuovo metodo `list_all` (sola lettura, query parametrizzata).
- Modifica: `backend/app/config.py` — nuovi campi `admin_user`, `admin_password`, `service_categories`.
- Modifica: `.env.example` — documenta `ADMIN_USER` / `ADMIN_PASSWORD`.
- Crea: `backend/app/admin/__init__.py` — pacchetto vuoto.
- Crea: `backend/app/admin/auth.py` — dependency `require_admin` (HTTP Basic).
- Crea: `backend/app/templates/appointments.html` — template Jinja2 con tabella e filtri.
- Crea: `backend/app/routers/admin.py` — router `GET /admin/appointments`.
- Modifica: `backend/app/main.py` — include il nuovo router.
- Modifica: `requirements.txt` — aggiunge `jinja2`.
- Modifica: `tests/test_repository.py` — test per `list_all`.
- Crea: `tests/test_admin_auth.py` — test unitari per `require_admin`.
- Crea: `tests/test_admin.py` — test di integrazione sulla rotta `/admin/appointments`.
- Modifica: `docs/NOTA_SCELTE_LIMITI.md` — riga sulla persistenza già presente dal primo slice.

Tutti i comandi vanno eseguiti dalla cartella `cai-voicebot/` (dove vivono `pyproject.toml` e `.venv/`).

---

### Task 1: Repository — `list_all` con filtri

**Files:**
- Modify: `backend/app/services/appointments/repository.py`
- Test: `tests/test_repository.py`

- [ ] **Step 1: Scrivi i test che falliscono**

Apri `tests/test_repository.py` e aggiungi in fondo al file:

```python
def test_list_all_empty_at_start(repo):
    assert repo.list_all() == []


def test_list_all_returns_rows_ordered_by_data_and_ora(repo):
    repo.create(codice="AAA1", servizio="Altro", data="2026-12-02", ora="09:00", nome="Mario")
    repo.create(codice="BBB2", servizio="Altro", data="2026-12-01", ora="10:00", nome="Luigi")
    repo.create(codice="CCC3", servizio="Altro", data="2026-12-01", ora="09:00", nome="Anna")

    rows = repo.list_all()
    assert [row["nome"] for row in rows] == ["Anna", "Luigi", "Mario"]


def test_list_all_filters_by_date_range(repo):
    repo.create(codice="AAA1", servizio="Altro", data="2026-12-01", ora="09:00", nome="Dentro")
    repo.create(codice="BBB2", servizio="Altro", data="2026-12-10", ora="09:00", nome="Fuori")

    rows = repo.list_all(data_da="2026-12-01", data_a="2026-12-05")
    assert [row["nome"] for row in rows] == ["Dentro"]


def test_list_all_filters_by_servizio(repo):
    repo.create(codice="AAA1", servizio="Anagrafe e stato civile", data="2026-12-01", ora="09:00", nome="Mario")
    repo.create(codice="BBB2", servizio="Altro", data="2026-12-01", ora="10:00", nome="Luigi")

    rows = repo.list_all(servizio="Altro")
    assert [row["nome"] for row in rows] == ["Luigi"]


def test_list_all_combines_date_and_servizio_filters(repo):
    repo.create(codice="AAA1", servizio="Altro", data="2026-12-01", ora="09:00", nome="Match")
    repo.create(codice="BBB2", servizio="Anagrafe e stato civile", data="2026-12-01", ora="10:00", nome="ServizioDiverso")
    repo.create(codice="CCC3", servizio="Altro", data="2026-12-10", ora="09:00", nome="DataFuoriRange")

    rows = repo.list_all(data_da="2026-12-01", data_a="2026-12-05", servizio="Altro")
    assert [row["nome"] for row in rows] == ["Match"]
```

- [ ] **Step 2: Esegui i test e verifica che falliscano**

Run: `.venv/bin/pytest tests/test_repository.py -v -k list_all`
Expected: FAIL con `AttributeError: 'AppointmentRepository' object has no attribute 'list_all'`

- [ ] **Step 3: Implementa `list_all`**

In `backend/app/services/appointments/repository.py`, aggiungi questo metodo alla classe `AppointmentRepository` (dopo `create`):

```python
    def list_all(
        self,
        *,
        data_da: str | None = None,
        data_a: str | None = None,
        servizio: str | None = None,
    ) -> list[sqlite3.Row]:
        clauses = []
        params: list[str] = []
        if data_da:
            clauses.append("data >= ?")
            params.append(data_da)
        if data_a:
            clauses.append("data <= ?")
            params.append(data_a)
        if servizio:
            clauses.append("servizio = ?")
            params.append(servizio)

        query = "SELECT codice, servizio, data, ora, nome, stato FROM appointments"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY data, ora"

        return self.conn.execute(query, params).fetchall()
```

Nota: i parametri sono passati con `?` (query parametrizzata), non con f-string — previene SQL injection. Le date sono stringhe ISO `YYYY-MM-DD`: il confronto lessicografico `>=`/`<=` coincide con l'ordine cronologico, niente parsing necessario.

- [ ] **Step 4: Esegui i test e verifica che passino**

Run: `.venv/bin/pytest tests/test_repository.py -v -k list_all`
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/appointments/repository.py tests/test_repository.py
git commit -m "feat(appointments): aggiunge list_all con filtri data e servizio al repository"
```

---

### Task 2: Settings — credenziali admin e categorie servizio

**Files:**
- Modify: `backend/app/config.py`
- Modify: `.env.example`

- [ ] **Step 1: Aggiungi i campi a `Settings`**

In `backend/app/config.py`, dentro la classe `Settings`, aggiungi (dopo `prenotazione_url`):

```python
    # Pannello admin (frontend minimale di sola lettura)
    admin_user: str = ""
    admin_password: str = ""
    service_categories: list[str] = [
        "Anagrafe e stato civile",
        "Autorizzazioni",
        "Imprese e commercio",
        "Tributi, finanze e contravvenzioni",
        "Altro",
    ]
```

Queste categorie corrispondono esattamente ai valori salvati nel campo `servizio` degli appuntamenti (il flusso di prenotazione registra la macro-categoria, non il nome del singolo servizio): il filtro fa match esatto, senza bisogno di mappature.

- [ ] **Step 2: Documenta le variabili in `.env.example`**

Apri `.env.example` e aggiungi in fondo:

```
# Pannello admin (frontend minimale prenotazioni — protezione HTTP Basic)
ADMIN_USER=
ADMIN_PASSWORD=
```

- [ ] **Step 3: Verifica che le impostazioni si carichino**

Run: `.venv/bin/python -c "from backend.app.config import settings; print(settings.admin_user, settings.service_categories)"`
Expected: stampa `` (stringa vuota) e la lista delle 5 categorie, nessun errore.

- [ ] **Step 4: Commit**

```bash
git add backend/app/config.py .env.example
git commit -m "feat(config): aggiunge credenziali admin e categorie servizio per il pannello prenotazioni"
```

---

### Task 3: Dependency di autenticazione `require_admin`

**Files:**
- Create: `backend/app/admin/__init__.py`
- Create: `backend/app/admin/auth.py`
- Test: `tests/test_admin_auth.py`

- [ ] **Step 1: Crea il pacchetto vuoto**

```bash
mkdir -p backend/app/admin
touch backend/app/admin/__init__.py
```

- [ ] **Step 2: Scrivi il test che fallisce**

Crea `tests/test_admin_auth.py`:

```python
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials

from backend.app.admin.auth import require_admin
from backend.app.config import settings


@pytest.fixture(autouse=True)
def admin_credentials(monkeypatch):
    monkeypatch.setattr(settings, "admin_user", "admin")
    monkeypatch.setattr(settings, "admin_password", "segreto")


def test_require_admin_accepts_correct_credentials():
    require_admin(HTTPBasicCredentials(username="admin", password="segreto"))


def test_require_admin_rejects_wrong_password():
    with pytest.raises(HTTPException) as exc_info:
        require_admin(HTTPBasicCredentials(username="admin", password="sbagliata"))
    assert exc_info.value.status_code == 401
    assert exc_info.value.headers["WWW-Authenticate"] == "Basic"


def test_require_admin_rejects_wrong_username():
    with pytest.raises(HTTPException) as exc_info:
        require_admin(HTTPBasicCredentials(username="qualcun_altro", password="segreto"))
    assert exc_info.value.status_code == 401
```

- [ ] **Step 3: Esegui i test e verifica che falliscano**

Run: `.venv/bin/pytest tests/test_admin_auth.py -v`
Expected: FAIL con `ModuleNotFoundError: No module named 'backend.app.admin.auth'`

- [ ] **Step 4: Implementa `require_admin`**

Crea `backend/app/admin/auth.py`:

```python
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from backend.app.config import settings

_security = HTTPBasic()


def require_admin(credentials: HTTPBasicCredentials = Depends(_security)) -> None:
    """Dependency FastAPI: protegge una rotta con HTTP Basic da .env."""
    user_ok = secrets.compare_digest(credentials.username, settings.admin_user)
    password_ok = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (user_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
            headers={"WWW-Authenticate": "Basic"},
        )
```

`secrets.compare_digest` confronta in tempo costante, evitando timing attack sul confronto delle credenziali.

- [ ] **Step 5: Esegui i test e verifica che passino**

Run: `.venv/bin/pytest tests/test_admin_auth.py -v`
Expected: 3 PASSED

- [ ] **Step 6: Commit**

```bash
git add backend/app/admin/__init__.py backend/app/admin/auth.py tests/test_admin_auth.py
git commit -m "feat(admin): aggiunge dependency require_admin con autenticazione HTTP Basic"
```

---

### Task 4: Template Jinja2 della pagina prenotazioni

**Files:**
- Create: `backend/app/templates/appointments.html`

- [ ] **Step 1: Crea la cartella e il template**

```bash
mkdir -p backend/app/templates
```

Crea `backend/app/templates/appointments.html`:

```html
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <title>Prenotazioni Servizi — Comune di Cherasco</title>
    <style>
        body { font-family: sans-serif; margin: 2rem; color: #222; }
        h1 { font-size: 1.4rem; }
        table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
        th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; }
        th { background: #f0f0f0; }
        form { margin-top: 1rem; }
        label { margin-right: 0.4rem; font-weight: bold; }
        input, select { margin-right: 1.2rem; }
    </style>
</head>
<body>
    <h1>Prenotazioni Servizi — Comune di Cherasco</h1>

    <form method="get" action="/admin/appointments">
        <label for="data_da">Dal</label>
        <input type="date" id="data_da" name="data_da" value="{{ data_da }}">

        <label for="data_a">Al</label>
        <input type="date" id="data_a" name="data_a" value="{{ data_a }}">

        <label for="servizio">Servizio</label>
        <select id="servizio" name="servizio">
            <option value="" {% if servizio == "" %}selected{% endif %}>Tutti</option>
            {% for categoria in categorie %}
            <option value="{{ categoria }}" {% if servizio == categoria %}selected{% endif %}>{{ categoria }}</option>
            {% endfor %}
        </select>

        <button type="submit">Filtra</button>
        <a href="/admin/appointments">Azzera</a>
    </form>

    {% if appuntamenti %}
    <table>
        <thead>
            <tr>
                <th>Data</th>
                <th>Ora</th>
                <th>Servizio</th>
                <th>Nome</th>
                <th>Codice</th>
                <th>Stato</th>
            </tr>
        </thead>
        <tbody>
            {% for appuntamento in appuntamenti %}
            <tr>
                <td>{{ appuntamento.data }}</td>
                <td>{{ appuntamento.ora }}</td>
                <td>{{ appuntamento.servizio }}</td>
                <td>{{ appuntamento.nome }}</td>
                <td>{{ appuntamento.codice }}</td>
                <td>{{ appuntamento.stato }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>Nessun appuntamento prenotato.</p>
    {% endif %}
</body>
</html>
```

`appuntamento.data` funziona anche se le righe sono `sqlite3.Row`: Jinja2 prova prima l'attributo, poi ricade sull'accesso per chiave (`row["data"]`), che `sqlite3.Row` supporta nativamente.

- [ ] **Step 2: Commit**

```bash
git add backend/app/templates/appointments.html
git commit -m "feat(admin): aggiunge template Jinja2 della pagina prenotazioni con filtri"
```

(Nessun test dedicato in questo task: il template viene verificato attraverso la rotta nel Task 5.)

---

### Task 5: Router `/admin/appointments` e wiring

**Files:**
- Create: `backend/app/routers/admin.py`
- Modify: `backend/app/main.py`
- Modify: `requirements.txt`
- Test: `tests/test_admin.py`

- [ ] **Step 1: Aggiungi `jinja2` alle dipendenze**

Apri `requirements.txt` e aggiungi una riga con `jinja2`. Poi installa:

Run: `.venv/bin/pip install jinja2 && .venv/bin/pip freeze | grep -i jinja2`
Expected: stampa la versione installata, es. `Jinja2==3.1.x`

- [ ] **Step 2: Scrivi i test che falliscono**

Crea `tests/test_admin.py`:

```python
import pytest

from backend.app.config import settings


@pytest.fixture(autouse=True)
def admin_credentials(monkeypatch):
    monkeypatch.setattr(settings, "admin_user", "admin")
    monkeypatch.setattr(settings, "admin_password", "segreto")


def test_appointments_requires_auth(client):
    resp = client.get("/admin/appointments")
    assert resp.status_code == 401
    assert resp.headers["www-authenticate"] == "Basic"


def test_appointments_rejects_wrong_credentials(client):
    resp = client.get("/admin/appointments", auth=("admin", "sbagliata"))
    assert resp.status_code == 401


def test_appointments_shows_empty_state_when_no_bookings(client):
    resp = client.get("/admin/appointments", auth=("admin", "segreto"))
    assert resp.status_code == 200
    assert "Prenotazioni Servizi" in resp.text
    assert "Nessun appuntamento prenotato" in resp.text


def test_appointments_lists_created_booking(client):
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Anagrafe e stato civile", "data": "2026-12-01", "ora": "09:00", "nome": "Mario Rossi"},
    )

    resp = client.get("/admin/appointments", auth=("admin", "segreto"))
    assert "Mario Rossi" in resp.text


def test_appointments_filters_by_servizio(client):
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Anagrafe e stato civile", "data": "2026-12-01", "ora": "09:00", "nome": "Mario Rossi"},
    )
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-01", "ora": "10:00", "nome": "Luigi Verdi"},
    )

    resp = client.get("/admin/appointments?servizio=Altro", auth=("admin", "segreto"))
    assert "Luigi Verdi" in resp.text
    assert "Mario Rossi" not in resp.text


def test_appointments_filters_by_date_range(client):
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-01", "ora": "09:00", "nome": "Dentro Range"},
    )
    client.post(
        "/tools/crea_appuntamento",
        json={"servizio": "Altro", "data": "2026-12-10", "ora": "09:00", "nome": "Fuori Range"},
    )

    resp = client.get(
        "/admin/appointments?data_da=2026-12-01&data_a=2026-12-05",
        auth=("admin", "segreto"),
    )
    assert "Dentro Range" in resp.text
    assert "Fuori Range" not in resp.text


def test_appointments_with_malformed_date_does_not_break(client):
    resp = client.get("/admin/appointments?data_da=non-una-data", auth=("admin", "segreto"))
    assert resp.status_code == 200
```

- [ ] **Step 3: Esegui i test e verifica che falliscano**

Run: `.venv/bin/pytest tests/test_admin.py -v`
Expected: FAIL con `404 Not Found` (la rotta `/admin/appointments` non esiste ancora) — gli assert su `status_code == 401`/`200` falliscono perché il client riceve 404.

- [ ] **Step 4: Implementa il router**

Crea `backend/app/routers/admin.py`:

```python
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from backend.app.admin.auth import require_admin
from backend.app.config import settings
from backend.app.deps import get_repo
from backend.app.services.appointments.repository import AppointmentRepository

router = APIRouter(prefix="/admin")

_templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def _validated_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        date.fromisoformat(value)
    except ValueError:
        return None
    return value


@router.get("/appointments")
def appointments(
    request: Request,
    data_da: str | None = None,
    data_a: str | None = None,
    servizio: str | None = None,
    repo: AppointmentRepository = Depends(get_repo),
    _: None = Depends(require_admin),
):
    data_da = _validated_date(data_da)
    data_a = _validated_date(data_a)
    servizio = servizio if servizio in settings.service_categories else None

    righe = repo.list_all(data_da=data_da, data_a=data_a, servizio=servizio)
    return _templates.TemplateResponse(
        request,
        "appointments.html",
        {
            "appuntamenti": righe,
            "categorie": settings.service_categories,
            "data_da": data_da or "",
            "data_a": data_a or "",
            "servizio": servizio or "",
        },
    )
```

Nota sulla validazione al confine: una data malformata o una categoria non in lista vengono ignorate silenziosamente (tornano `None`), così la pagina mostra semplicemente l'elenco non filtrato invece di rompersi con un errore.

- [ ] **Step 5: Includi il router in `main.py`**

Apri `backend/app/main.py` e modificalo così:

```python
from fastapi import FastAPI

from backend.app.routers import admin, health, tools

app = FastAPI(title="CAI Voicebot Backend")
app.include_router(health.router)
app.include_router(tools.router)
app.include_router(admin.router)
```

- [ ] **Step 6: Esegui i test e verifica che passino**

Run: `.venv/bin/pytest tests/test_admin.py -v`
Expected: 7 PASSED

- [ ] **Step 7: Esegui l'intera suite per verificare che non ci siano regressioni**

Run: `.venv/bin/pytest -v`
Expected: tutti i test PASSED (i 46 esistenti + i nuovi di questo piano)

- [ ] **Step 8: Commit**

```bash
git add backend/app/routers/admin.py backend/app/main.py requirements.txt tests/test_admin.py
git commit -m "feat(admin): aggiunge rotta GET /admin/appointments con filtri e protezione HTTP Basic"
```

---

### Task 6: Verifica manuale nel browser

**Files:** nessuno (solo verifica)

- [ ] **Step 1: Imposta le credenziali admin nel `.env` locale**

Apri `cai-voicebot/.env` e aggiungi (sostituendo con valori a tua scelta):

```
ADMIN_USER=admin
ADMIN_PASSWORD=scegli-una-password
```

- [ ] **Step 2: Avvia il backend**

Run: `.venv/bin/uvicorn backend.app.main:app --reload`
Expected: il server si avvia su `http://127.0.0.1:8000`

- [ ] **Step 3: Apri la pagina nel browser**

Vai a `http://127.0.0.1:8000/admin/appointments`. Il browser chiede username e password (popup nativo di HTTP Basic): inserisci le credenziali impostate al passo 1.

Verifica:
- la pagina mostra il titolo "Prenotazioni Servizi — Comune di Cherasco";
- la tabella mostra gli appuntamenti già presenti in `data/appointments.db` (6 righe di test, secondo l'esplorazione fatta in fase di design);
- il menu a tendina "Servizio" elenca le 5 categorie più "Tutti";
- selezionando una categoria e premendo "Filtra", la tabella mostra solo le righe di quella categoria e l'URL contiene `?servizio=...`;
- impostando "Dal"/"Al" e premendo "Filtra", la tabella mostra solo le righe nell'intervallo;
- "Azzera" riporta alla vista senza filtri.

- [ ] **Step 4: Verifica la protezione**

Apri una finestra in incognito e vai allo stesso URL senza inserire credenziali (annulla il popup): il browser deve mostrare un errore "401 Unauthorized", non la pagina.

- [ ] **Step 5: Ferma il server**

Premi `Ctrl+C` nel terminale dove gira `uvicorn`.

(Nessun commit: questo task è solo verifica manuale, non produce modifiche al codice.)

---

### Task 7: Nota nei documenti del test

**Files:**
- Modify: `docs/NOTA_SCELTE_LIMITI.md`

- [ ] **Step 1: Aggiungi la riga sulla persistenza già presente**

Apri `docs/NOTA_SCELTE_LIMITI.md` e, nella sezione "## Scelte effettuate", aggiungi come ultimo punto dell'elenco (prima della riga vuota che precede "## Limitazioni"):

```
- Persistenza su database fin dal primo slice: gli appuntamenti vivono in SQLite (non in
  memoria) sin dall'inizio del progetto — uno dei due elementi aggiuntivi richiesti dal test era
  quindi già coperto dall'architettura di base, non un'aggiunta successiva.
```

- [ ] **Step 2: Verifica visivamente il file**

Run: `head -25 docs/NOTA_SCELTE_LIMITI.md`
Expected: la nuova riga compare in fondo all'elenco "Scelte effettuate", formattata come gli altri punti.

- [ ] **Step 3: Commit**

```bash
git add docs/NOTA_SCELTE_LIMITI.md
git commit -m "docs: chiarisce che la persistenza su database era già presente dal primo slice"
```

---

## Riepilogo verifiche finali

- [ ] `.venv/bin/pytest -v` — tutta la suite verde (esistenti + nuovi test di repository, auth, admin).
- [ ] Verifica manuale nel browser completata (Task 6): pagina, filtri, protezione HTTP Basic.
- [ ] `git log --oneline -8` mostra i commit di questo piano in ordine: repository → config → auth → template → router → docs.
