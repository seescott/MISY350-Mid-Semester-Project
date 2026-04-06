import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time


st.set_page_config("AI Expense Tracker", layout="wide", page_icon="💰", initial_sidebar_state="expanded") ## come back and add icon

users_path = Path("users.json")
expenses_path = Path("expenses.json")

def get_expenses(email):
    return [e for e in expenses if e["email"] == email]

if users_path.exists():
    try:
        with open(users_path, "r") as f:
            users = json.load(f)
    except:
        users = []
else:
    users = [{
        "email": "useremail@gmail.com",
        "full_name": "John Doe",
        "password": "12345",
        "role": "admin",
    }]
    with open(users_path, "w") as f:
        json.dump(users, f)


if expenses_path.exists():
    try:
        with open(expenses_path, "r") as f:
            expenses = json.load(f)
    except:
        expenses = []
else:
    expenses = []

if "page" not in st.session_state:
    st.session_state.page = "login"
    
if "user" not in st.session_state:
    st.session_state.user = None

if "edit_expense" not in st.session_state:
    st.session_state.edit_expense = None

def valid_email(email):
    return "@" in email and "." in email and len(email) >= 5

def valid_password(password):
    return len(password) >= 5

##Login guard reccomended by AI checker
login_guard = ["dashboard", "add_expense", "AI_Chat", "admin", "edit_expense"]
if st.session_state["page"] in login_guard and not st.session_state["user"]:
        st.warning("Please log in first")
        st.session_state["page"] = "login"
        st.rerun()

##Sidebar panel
with st.sidebar:
    if st.session_state["user"]:
        st.write(f"Logged in as: {st.session_state['user']['email']}")

        if st.button ("Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()

        if st.button("Add Expense"):
            st.session_state["page"] = "add_expense"
            st.rerun()

        if st.button("AI Chat"):
            st.session_state["page"] = "AI_Chat"
            st.rerun()


        if st.session_state["user"]["role"].lower() == "admin":
            if st.button("Admin Features"):
                st.session_state["page"] = "admin"
                st.rerun()


        if st.button("Logout"):
            st.session_state["user"] = None
            st.session_state["page"] = "login"
            st.rerun()


##Logging in 
if st.session_state["page"] == "login":
    st.title("Welcome to AI Expense Tracker")

    st.subheader("Login")
    with st.container(border=True):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login",type="primary"):
         with st.spinner("Logging in..."):
            time.sleep(2)
            found_user = None
            for user in users:
                if user["email"].lower() == email.lower() and user["password"] == password:
                    found_user = user
                    break

            if found_user:
                st.success(f"Welcome back, {found_user['email']}!")
                st.session_state["user"] = found_user
                st.session_state["page"] = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    ##Creating a new account
    st.subheader("Create new account")
    with st.container(border=True):
        new_name = st.text_input("Full Name", key = "register_name")
        new_email = st.text_input("Email", key = "register_email")
        new_password = st.text_input("Password", type="password", key = "register_password")
        new_role = st.radio("Role", options=["admin", "user"], horizontal=True)

        if st.button("Create Account", key= "register_btn"):
            if new_name=="" or new_email=="" or new_password=="":
                st.error("Please fill in all fields")
            elif not valid_email(new_email):
                st.error("Enter a valid email")
            elif any(u["email"].lower() == new_email.lower() for u in users):
                st.error("Email already exists")
            elif not valid_password(new_password):
                st.error("Password must be at least 5 characters")

            else:
                with st.spinner("Creating account..."):
                    time.sleep(2)
                    users.append({
                        "full_name": new_name,
                        "email": new_email,
                        "password": new_password,
                        "role": new_role.lower()
                    })
                    
                    with open(users_path, "w") as f:
                        json.dump(users,f)

                st.success("Account created!")
                st.rerun()


##Dashboard Page    
elif st.session_state["page"] == "dashboard":
    st.title("💵 Expense Dashboard 💵")
    st.write("---")

    user_email = st.session_state.user["email"]
    user_expenses = get_expenses(user_email)

    if len(user_expenses) == 0:
        st.info("No expenses found")
    else:
        
       
##Calculations
        total_spent = 0

        for e in user_expenses:
            total_spent += e["amount"]

        total_transactions = len(user_expenses)

        if total_transactions >0:
            avg = total_spent / total_transactions
        else:
            avg = 0
        
        with st.container(border=True):
            st.subheader("Summary 📋")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Spent", f"${total_spent:.2f}")
            col2.metric("Total Transactions", total_transactions)
            col3.metric("Average Transaction", f"${avg:.2f}")

        st.divider()

##Expenses by Category
        category_amounts = {}

        for e in user_expenses:
            category = e["category"]
            amount = e["amount"]

            if category in category_amounts:
                category_amounts[category] += amount  
            else:
                category_amounts[category] = amount

        col1, col2 = st.columns(2)
        
        ##Test this once I add the adding expenses function

        with col1:
            with st.container(border=True):
                st.subheader("Expenses by Category 📊")
                if category_amounts:
                    st.bar_chart(category_amounts)
                else: 
                    st.info("No expenses yet")

    ##Highest and lowest expenses
        with col2:
            with st.container(border=True):
                st.subheader("📈 Highest and Lowest Expenses 📉")
                
                highest = user_expenses[0]
                lowest = user_expenses[0]

                for e in user_expenses:
                    if e["amount"] > highest["amount"]:
                        highest = e
                    if e["amount"] < lowest["amount"]:
                        lowest = e

                st.write(f"Highest Expense: ${highest['amount']:.2f} {highest['category']}")
                st.write(f"Lowest Expense: ${lowest['amount']:.2f} {lowest['category']}")

        ##Also test this once I add the adding expenses function
        st.write("---")
    ##All Expenses
        st.subheader("All Expenses 🧾")
        for e in user_expenses:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2,1,3])
                col1.write(f"Category: {e['category']}")
                col2.write(f"Amount: ${e['amount']:.2f}")
                col3.write(f"Note: {e['note']}")

##Adding expenses page
elif st.session_state["page"] == "add_expense":
    st.title("Add New Expense")

    amount = st.number_input("Amount", min_value = 0.01)
    category = st.selectbox("Category", options = ["Food", "Transportation", "Bills", "Entertainment", "Other"])
    note = st.text_area("Note (optional)")

    if st.button("Add Expense", key = "add_expense_btn"):
        if amount <= 0:
            st.error("Amount must be greater than 0")
        else:
            with st.spinner("Adding expense..."):
                time.sleep(2)

                expenses.append({
                    "id": str(uuid.uuid4())[:6],
                    "email": st.session_state["user"]["email"],
                    "amount": amount,
                    "category": category,
                    "note": note,})
                
                with open(expenses_path, "w") as f:
                    json.dump(expenses, f)
            st.success("Expense added!")
            st.rerun()
            ##Adding expenses page need to add a loading adding expense spinner

##AI Chat Page
elif st.session_state["page"] == "AI_Chat":
    st.title("AI Assistant 💻")

    user_input = st.text_input("Ask a question")
    if st.button("Ask"):
        user_email = st.session_state.user["email"]
        user_expenses = [e for e in expenses if e["email"] == user_email]

        if user_input =="How much did I spend this month?":
            total = sum(e["amount"] for e in user_expenses)
            st.success(f"You spent ${total:.2f} this month!")

        elif user_input == "List my expenses":
            st.dataframe(user_expenses)

        elif user_input =="How many transactions did I make?":
            count = len(user_expenses)
            st.success(f"You made {count} transactions this month!")

        elif user_input == "How many categories did I spend in?":
            categories = []
            for e in user_expenses:
                if e["category"] not in categories:
                    categories.append(e["category"])
            st.success(f"You spent in {len(categories)} categories this month!")

        elif user_input =="How much did I spend on food?":
            food_total = 0
            for e in user_expenses:
                if e["category"] == "Food":
                    food_total += e["amount"]
            st.success(f"You spent ${food_total:.2f} on food this month!")
        else:
            st.warning("Try a supported question")

##Admin Page
elif st.session_state["page"] == "admin":
    if not st.session_state["user"] or st.session_state["user"]["role"].lower() != "admin":
        st.error("This is only accessible to admins")
        st.stop()

    st.title("Admin Dashboard 👩‍🏫")

    user_emails = [u["email"] for u in users]
    selected_user = st.selectbox("Select User", user_emails)

    if selected_user:
        user_expenses = [e for e in expenses if e["email"] == selected_user]

        st.subheader(f"{selected_user}'s Expenses")
        for e in user_expenses:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns(4)
                col1.write(f"Amount: ${e['amount']:.2f}")
                col2.write(f"Category: {e['category']}")
                col3.write(f"Note: {e['note']}")

                if col4.button("Delete", key=f"delete_{e['id']}"):
                    expenses.remove(e)
                    with open(expenses_path, "w") as f:
                        json.dump(expenses, f)
                    st.success("Expense deleted")
                    st.rerun()

                if col4.button("Edit", key=f"edit_{e['id']}"):
                    st.session_state["edit_expense"] = e
                    st.session_state["page"] = "edit_expense"
                    st.rerun()

##Editing expenses section
elif st.session_state["page"] == "edit_expense":
    st.title("Edit Expense")
    if not st.session_state["user"] or st.session_state["user"]["role"].lower() != "admin":
        st.error("Admins only")
        st.stop()

    e = st.session_state.edit_expense
    if e is None:
        st.error("No expense selected")
        st.session_state["page"] = "admin"

    amount = st.number_input("Amount", value=e["amount"])
    category = st.selectbox("Category", options = ["Food", "Transportation", "Bills", "Entertainment", "Other"])
    note = st.text_area("Note (optional)")

    if st.button("Save Changes"):
        for expense in expenses:
            if expense["id"] == e["id"]:
                expense["amount"] = amount
                expense["category"] = category
                expense["note"] = note

        with open(expenses_path, "w") as f:
            json.dump(expenses, f)

        st.success("Expense updated")
        st.session_state["page"] = "admin"
        st.rerun()






