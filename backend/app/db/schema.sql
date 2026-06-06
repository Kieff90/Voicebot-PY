CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice TEXT NOT NULL UNIQUE,
    servizio TEXT NOT NULL,
    data TEXT NOT NULL,
    ora TEXT NOT NULL,
    nome TEXT NOT NULL,
    stato TEXT NOT NULL DEFAULT 'confermato',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (servizio, data, ora)
);
