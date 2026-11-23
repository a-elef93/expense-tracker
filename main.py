from datetime import date
from pathlib import Path

from database import Database
from transaction import Transaction
from transaction_repository import TransactionRepository


def main():
    database = Database(Path(__file__).with_name("expenses.sqlite3"))
    database.initialize()
    repository = TransactionRepository(database)

    print("1. Add transaction")
    print("2. List transactions")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        kind = input("Type (income/expense): ").strip().lower()
        if kind not in ("income", "expense"):
            print("Choose income or expense.")
            return

        try:
            amount_cents = int(input("Amount in cents (e.g. 350): "))
        except ValueError:
            print("Enter a whole number of cents.")
            return

        category = input("Category: ").strip().lower()
        if not 0 < amount_cents <= 2**63 - 1 or not category:
            print("Enter a valid positive amount and a category.")
            return

        transaction = Transaction(kind, amount_cents, category, date.today().isoformat())
        transaction_id = repository.add_transaction(transaction)
        print(f"Saved transaction #{transaction_id}.")

    elif choice == "2":
        rows = repository.list_transactions()
        if not rows:
            print("No transactions yet.")

        for transaction_id, kind, amount_cents, category, entry_date in rows:
            euros, cents = divmod(amount_cents, 100)
            print(f"#{transaction_id} | {entry_date} | {kind} | €{euros}.{cents:02d} | {category}")

    else:
        print("Choose 1 or 2.")


if __name__ == "__main__":
    main()