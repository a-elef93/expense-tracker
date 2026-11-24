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

    def delete_transaction(self, entry_id):
        connection = self.database.connect()
        try:
            cursor = connection.execute(
                "DELETE FROM transactions WHERE id = ?", (entry_id,)
            )
            connection.commit()
            return cursor.rowcount == 1
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

    def monthly_totals(self, month):
        connection = self.database.connect()
        try:
            rows = connection.execute(
                """
                SELECT kind, amount_cents
                FROM transactions
                WHERE substr(entry_date, 1, 7) = ?
                """,
                (month,),
            ).fetchall()
        finally:
            connection.close()

        totals = {"income": 0, "expense": 0}
        for kind, amount_cents in rows:
            totals[kind] += amount_cents

        return totals

    def update_transaction(self, entry_id, kind, cents, category):
        connection = self.database.connect()
        try:
            cursor = connection.execute(
                """
                UPDATE transactions
                SET kind = ?, amount_cents = ?, category = ?
                WHERE id = ?
                """,
                (kind, cents, category, entry_id),
            )
            connection.commit()
            return cursor.rowcount == 1
        finally:
            connection.close()