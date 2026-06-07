import sqlite3


class AppointmentRepository:
    """Accesso dati appuntamenti. Nessuna business rule qui."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def booked_slots(self, servizio: str, data: str) -> set[str]:
        rows = self.conn.execute(
            "SELECT ora FROM appointments WHERE servizio = ? AND data = ?",
            (servizio, data),
        ).fetchall()
        return {row[0] for row in rows}

    def create(
        self, *, codice: str, servizio: str, data: str, ora: str, nome: str
    ) -> None:
        self.conn.execute(
            "INSERT INTO appointments (codice, servizio, data, ora, nome) "
            "VALUES (?, ?, ?, ?, ?)",
            (codice, servizio, data, ora, nome),
        )
        self.conn.commit()

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
