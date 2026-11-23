class Transaction:
    def __init__(self, kind, amount_cents, category, entry_date):
        self.kind = kind
        self.amount_cents = amount_cents
        self.category = category
        self.entry_date = entry_date