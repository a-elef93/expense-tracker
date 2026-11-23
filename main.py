from database import Database



def main():
    database = Database("expenses.sqlite3")
    database.initialize()
    print("Database is ready.")


if __name__ == "__main__":
    main()