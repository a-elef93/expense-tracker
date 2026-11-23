import sqlite3

connection = sqlite3.connect("expenses.sqlite3")
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



connection.close()

print("Database is ready.")