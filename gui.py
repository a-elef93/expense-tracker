import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from database import Database
from main import format_euros
from transaction_repository import TransactionRepository
from datetime import date
from transaction import Transaction

import re
from decimal import Decimal


class ExpenseTrackerApp:
    def __init__(self, window, repository):
        self.repository = repository
        window.title("Expense Tracker")
        window.geometry("760x420")

        form = ttk.Frame(window, padding=12)
        form.pack(fill="x")

        ttk.Label(form, text="Type").grid(row=0, column=0, padx=4)
        self.kind = ttk.Combobox(
            form, values=("Expense", "Income"), state="readonly", width=10
        )
        self.kind.set("Expense")
        self.kind.grid(row=1, column=0, padx=4)

        ttk.Label(form, text="Amount (€)").grid(row=0, column=1, padx=4)
        self.amount = ttk.Entry(form, width=16)
        self.amount.grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Category").grid(row=0, column=2, padx=4)
        self.category = ttk.Entry(form, width=20)
        self.category.grid(row=1, column=2, padx=4)

        ttk.Button(form, text="Save", command=self.save_transaction).grid(
            row=1, column=3, padx=4
        )

        summary = ttk.Frame(window, padding=(12, 0))
        summary.pack(fill="x")

        ttk.Label(summary, text="Month (YYYY-MM)").pack(side="left")
        self.month = ttk.Entry(summary, width=9)
        self.month.insert(0, date.today().isoformat()[:7])
        self.month.pack(side="left", padx=6)

        ttk.Button(summary, text="Show Summary", command=self.refresh_summary).pack(
            side="left"
        )

        self.summary_label = ttk.Label(window, padding=(12, 8))
        self.summary_label.pack(fill="x")
        self.refresh_summary()
        columns = ("ID", "Date", "Type", "Category", "Amount")
        self.table = ttk.Treeview(window, columns=columns, show="headings")

        for column, width in zip(columns, (55, 120, 100, 240, 110)):
            self.table.heading(column, text=column)
            self.table.column(column, width=width)

        self.table.pack(fill="both", expand=True, padx=12, pady=12)
        self.refresh_table()

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for entry_id, kind, cents, category, entry_date in self.repository.list_transactions():
            self.table.insert(
                "",
                "end",
                values=(
                    entry_id,
                    entry_date,
                    kind.capitalize(),
                    category[:1].upper() + category[1:],
                    format_euros(cents),
                ),
            )
    def refresh_summary(self):
        month = self.month.get().strip()

        try:
            first_day = date.fromisoformat(f"{month}-01")
            if first_day.isoformat()[:7] != month:
                raise ValueError
        except ValueError:
            self.summary_label.config(text="Enter a valid month, e.g. 2026-11.")
            return

        totals = self.repository.monthly_totals(month)
        income = totals["income"]
        expenses = totals["expense"]

        self.summary_label.config(
            text=(
                f"Income: {format_euros(income)}    "
                f"Expenses: {format_euros(expenses)}    "
                f"Balance: {format_euros(income - expenses)}"
            )
        )


    def save_transaction(self):
        amount_text = self.amount.get().strip().replace(",", ".")

        if not re.fullmatch(r"[0-9]{1,17}(\.[0-9]{1,2})?", amount_text):
            messagebox.showerror(
                "Invalid amount",
                "Enter an amount in euros with up to two decimal places.",
            )
            return

        cents = int(Decimal(amount_text) * 100)

        category = self.category.get().strip().lower()
        if not 0 < cents <= 2**63 - 1 or not category:
            messagebox.showerror("Invalid transaction", "Enter a positive amount and a category.")
            return

        transaction = Transaction(
            self.kind.get().lower(), cents, category, date.today().isoformat()
        )
        self.repository.add_transaction(transaction)
        self.refresh_table()
        self.refresh_summary()
        self.amount.delete(0, tk.END)
        self.category.delete(0, tk.END)


def main():
    database = Database(Path(__file__).with_name("expenses.sqlite3"))
    database.initialize()

    window = tk.Tk()
    ExpenseTrackerApp(window, TransactionRepository(database))
    window.mainloop()


if __name__ == "__main__":
    main()