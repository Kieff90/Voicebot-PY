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
