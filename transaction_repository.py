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