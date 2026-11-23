class TransactionRepository:
    def __init__(self, database):
        self.database = database

    def add_transaction(self, transaction):
        connection = self.database.connect()

        try:
            cursor = connection.execute(
                """
                INSERT INTO transactions (kind, amount_cents, category, entry_date)
                VALUES (?, ?, ?, ?)
                """,
                (
                    transaction.kind,
                    transaction.amount_cents,
                    transaction.category,
                    transaction.entry_date,
                ),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def list_transactions(self):
        connection = self.database.connect()

        try:
            cursor = connection.execute("""
                SELECT id, kind, amount_cents, category, entry_date
                FROM transactions
                ORDER BY id DESC
            """)
            return cursor.fetchall()
        finally:
            connection.close()