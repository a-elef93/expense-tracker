import sqlite3

connection = sqlite3.connect("expenses.sqlite3")
connection.close()

print("Database is ready.")