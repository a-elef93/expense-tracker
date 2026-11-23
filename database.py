import sqlite3


class Database:
    def __init__(self, path):
        self.path = path

    def initialize(self):
        connection = sqlite3.connect(self.path)
        try:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    kind TEXT NOT NULL CHECK (kind IN ('income', 'expense')),
                    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
                    category TEXT NOT NULL,
                    entry_date TEXT NOT NULL
                )
            """)
            connection.commit()
        finally:
            connection.close()


def add_transaction(connection, kind, amount_cents, category, entry_date):
    cursor = connection.execute(
        """
        INSERT INTO transactions (kind, amount_cents, category, entry_date)
        VALUES (?, ?, ?, ?)
        """,
        (kind, amount_cents, category, entry_date),
    )
    connection.commit()
    return cursor.lastrowid