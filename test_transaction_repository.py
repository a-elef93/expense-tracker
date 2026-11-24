import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from database import Database
from transaction import Transaction
from transaction_repository import TransactionRepository


class TransactionRepositoryTest(unittest.TestCase):
    def test_add_update_and_delete_expense(self):
        with TemporaryDirectory() as folder:
            database = Database(Path(folder) / "test.sqlite3")
            database.initialize()
            repository = TransactionRepository(database)

            expense = Transaction("expense", 100, "coffee", "2026-11-24")
            entry_id = repository.add_transaction(expense)
            self.assertEqual(repository.monthly_totals("2026-11")["expense"], 100)

            self.assertTrue(
                repository.update_transaction(entry_id, "expense", 250, "coffee")
            )
            self.assertEqual(
                repository.list_transactions(),
                [(entry_id, "expense", 250, "coffee", "2026-11-24")],
            )
            self.assertEqual(repository.monthly_totals("2026-11")["expense"], 250)

            self.assertTrue(repository.delete_transaction(entry_id))
            self.assertEqual(repository.list_transactions(), [])
            self.assertEqual(repository.monthly_totals("2026-11")["expense"], 0)