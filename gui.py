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
        self.editing_id = None
        window.title("Expense Tracker")
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        width = min(960, screen_width)
        height = min(540, screen_height)

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")

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

        self.save_button = ttk.Button(form, text="Save", command=self.save_transaction)
        self.save_button.grid(row=1, column=3, padx=4)

        ttk.Button(form, text="Edit Selected", command=self.edit_selected).grid(
            row=2, column=3, padx=4, pady=4
        )

        ttk.Button(form, text="Cancel Edit", command=self.clear_form).grid(
            row=2, column=4, padx=4, pady=4
        )

        ttk.Button(form, text="Delete Selected", command=self.delete_selected).grid(
            row=1, column=4, padx=4
        )

        summary = ttk.Frame(window, padding=(12, 0))
        summary.pack(fill="x")

        ttk.Label(summary, text="Month (MM-YYYY)").pack(side="left")
        self.month = ttk.Entry(summary, width=9)
        self.month.insert(0, date.today().strftime("%m-%Y"))
        self.month.pack(side="left", padx=6)

        ttk.Button(summary, text="Show Summary", command=self.refresh_summary).pack(
            side="left"
        )

        self.summary_label = ttk.Label(window, padding=(12, 8))
        self.summary_label.pack(fill="x")
        self.refresh_summary()
        columns = ("ID", "Date", "Type", "Category", "Amount")
        self.table = ttk.Treeview(
            window,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

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
                iid=str(entry_id),
                values=(
                    entry_id,
                    entry_date,
                    kind.capitalize(),
                    category[:1].upper() + category[1:],
                    format_euros(cents),
                ),
            )
    def refresh_summary(self):
        month_text = self.month.get().strip()

        try:
            month, year = month_text.split("-")
            first_day = date.fromisoformat(f"{year}-{month}-01")
        except ValueError:
            self.summary_label.config(text="Enter a valid month, e.g. 11-2026.")
            return

        totals = self.repository.monthly_totals(first_day.isoformat()[:7])

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

        kind = self.kind.get().lower()

        if self.editing_id is None:
            transaction = Transaction(kind, cents, category, date.today().isoformat())
            self.repository.add_transaction(transaction)
        else:
            updated = self.repository.update_transaction(
                self.editing_id, kind, cents, category
            )
            if not updated:
                messagebox.showinfo(
                    "Transaction Missing", "This transaction no longer exists."
                )

        self.refresh_table()
        self.refresh_summary()
        self.clear_form()


    def delete_selected(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Select a Transaction", "Select a row first.")
            return

        entry_id = int(selection[0])
        if not messagebox.askyesno(
            "Delete Transaction", f"Delete transaction #{entry_id}?"
        ):
            return

        deleted = self.repository.delete_transaction(entry_id)
        self.refresh_table()
        self.refresh_summary()

        if not deleted:
            messagebox.showinfo("Transaction Missing", "This transaction no longer exists.")

    def edit_selected(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Select a Transaction", "Select a row first.")
            return

        entry_id, _, kind, category, amount = self.table.item(selection[0], "values")
        self.editing_id = int(entry_id)
        self.kind.set(kind)
        self.amount.delete(0, tk.END)
        self.amount.insert(0, amount.removeprefix("€"))
        self.category.delete(0, tk.END)
        self.category.insert(0, category)
        self.save_button.configure(text="Update")

    def clear_form(self):
        self.editing_id = None
        self.amount.delete(0, tk.END)
        self.category.delete(0, tk.END)
        self.save_button.configure(text="Save")




def main():
    database = Database(Path(__file__).with_name("expenses.sqlite3"))
    database.initialize()

    window = tk.Tk()
    ExpenseTrackerApp(window, TransactionRepository(database))
    window.mainloop()


if __name__ == "__main__":
    main()