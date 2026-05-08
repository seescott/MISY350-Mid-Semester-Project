import uuid


class ExpenseService:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.expenses = self.data_manager.load_expenses()

    def get_all_expenses(self):
        return self.expenses

    def get_user_expenses(self, email):
        return [expense for expense in self.expenses if expense["email"] == email]

    def add_expense(self, email, amount, category, note):
        new_expense = {
            "id": str(uuid.uuid4())[:6],
            "email": email,
            "amount": amount,
            "category": category,
            "note": note
        }

        self.expenses.append(new_expense)
        self.data_manager.save_expenses(self.expenses)

    def delete_expense(self, expense_id):
        self.expenses = [
            expense for expense in self.expenses
            if expense["id"] != expense_id
        ]
        self.data_manager.save_expenses(self.expenses)

    def update_expense(self, expense_id, amount, category, note):
        for expense in self.expenses:
            if expense["id"] == expense_id:
                expense["amount"] = amount
                expense["category"] = category
                expense["note"] = note

        self.data_manager.save_expenses(self.expenses)

    def get_summary(self, email):
        user_expenses = self.get_user_expenses(email)

        total_spent = sum(expense["amount"] for expense in user_expenses)
        total_transactions = len(user_expenses)

        if total_transactions > 0:
            average = total_spent / total_transactions
        else:
            average = 0

        return total_spent, total_transactions, average

    def get_category_totals(self, email):
        user_expenses = self.get_user_expenses(email)
        category_totals = {}

        for expense in user_expenses:
            category = expense["category"]
            amount = expense["amount"]

            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        return category_totals

    def get_highest_lowest(self, email):
        user_expenses = self.get_user_expenses(email)

        if len(user_expenses) == 0:
            return None, None

        highest = user_expenses[0]
        lowest = user_expenses[0]

        for expense in user_expenses:
            if expense["amount"] > highest["amount"]:
                highest = expense

            if expense["amount"] < lowest["amount"]:
                lowest = expense

        return highest, lowest