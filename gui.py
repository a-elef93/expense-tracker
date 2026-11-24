import tkinter as tk
from pathlib import Path
from tkinter import ttk

from database import Database
from main import format_euros
from transaction_repository import TransactionRepository


class ExpenseTrackerApp:
    def __init__(self, window, repository):
        window.title("Expense Tracker")
        window.geometry("760x420")

        columns = ("ID", "Date", "Type", "Category", "Amount")
        table = ttk.Treeview(window, columns=columns, show="headings")

        for column, width in zip(columns, (55, 120, 100, 240, 110)):
            table.heading(column, text=column)
            table.column(column, width=width)

        for entry_id, kind, cents, category, entry_date in repository.list_transactions():
            table.insert(
                "",
                "end",
                values=(entry_id, entry_date, kind, category, format_euros(cents)),
            )

        table.pack(fill="both", expand=True, padx=12, pady=12)


def main():
    database = Database(Path(__file__).with_name("expenses.sqlite3"))
    database.initialize()

    window = tk.Tk()
    ExpenseTrackerApp(window, TransactionRepository(database))
    window.mainloop()


if __name__ == "__main__":
    main()