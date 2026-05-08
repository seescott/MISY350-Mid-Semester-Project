import json
from pathlib import Path


class DataManager:
    def __init__(self):
        self.users_path = Path("users.json")
        self.expenses_path = Path("expenses.json")

    def load_users(self):
        if self.users_path.exists():
            with open(self.users_path, "r") as file:
                return json.load(file)
        return []

    def save_users(self, users):
        with open(self.users_path, "w") as file:
            json.dump(users, file, indent=4)

    def load_expenses(self):
        if self.expenses_path.exists():
            with open(self.expenses_path, "r") as file:
                return json.load(file)
        return []

    def save_expenses(self, expenses):
        with open(self.expenses_path, "w") as file:
            json.dump(expenses, file, indent=4)