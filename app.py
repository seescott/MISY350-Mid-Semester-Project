import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

st.set_page_config("AI Expense Tracker", layout="wide", page_icon="", initial_sidebar_state="expanded") ## come back and add icon

users_path = Path("users.json")
expenses_path = Path("expenses.json")

json_path_users = Path("users.json")
json_path_expenses = Path("expenses.json")

if users_path.exists():
    with open(users_path, "r") as f:
        users = json.load(f)
else:
    users = [
        {
        "email": "useremail@gmail.com",
        "full_name": "John Doe",
        "password": "12345",
        "role": "admin",
    }
    ]
    with open(users_path, "w") as f:
        json.dump(users, f)

if expenses_path.exists():
    with open(expenses_path, "r") as f:
        expenses = json.load(f)
else:
    expenses = []

if "page" not in st.session_state:
    st.session_state.page = "login"
    
if "user" not in st.session_state:
    st.session_state.user = None
##Sidebar panel
with st.sidebar:
    if st.session_state["user"]:
        st.write(f"Logged in as: {st.session_state['user']['email']}")

        if st.button ("Dashboard", key = "dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()

        if st.button("Add Expense", key = "add_expense"):
            st.session_state["page"] = "add_expense"
            st.rerun()
        
        if st.button("AI Chat", key = "ai_chat"):
            st.session_state["page"] = "ai_chat"
            st.rerun()

        if st.session_state["user"]["role"] == "admin":
            if st.button("admin"):
                st.session_state["page"] = "admin"
                st.rerun()

        if st.button("Logout", key="logout"):
            st.session_state["user"] = None
            st.session_state["page"] = "login"
            st.rerun()

##Logging in 
if st.session_state["page"] == "login":
    st.title("Welcome to AI Expense Tracker")
    st.subheader("Login")
    with st.container(border=True):
        email = st.text_input("Email", key = "email")
        password = st.text_input("Password", type="password", key = "password")
    
    if st.button("Login",type="primary", key = "login_button"):
         with st.spinner("Logging in..."):
            time.sleep(2)

            found_user = None
            for user in users:
                if user["email"].strip().lower() == email.strip().lower() and user["password"] == password:
                    found_user = user
                    break

            if found_user:
                st.success(f"Welcome back, {found_user['email']}!")
                st.session_state["logged_in"] = True
                st.session_state["user"] = found_user
                st.session_state["page"] = "dashboard"
                time.sleep(2)
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    ##Creating a new account
    st.subheader("Create new account")
    with st.container(border=True):
        new_name = st.text_input("Full Name", key= "full_name")
        new_email = st.text_input("Email", key= "email_register")
        new_password = st.text_input("Password", type="password", key= "password_creation")
        new_role = st.radio("Role", options=["Admin", "User"], key = "role_select", horizontal=True)

        if st.button("Create Account", key= "register_btn"):
            with st.spinner("Creating account..."):
                time.sleep(2) 
                users.append({
                    "full_name": new_name,
                    "email": new_email,
                    "password": new_password,
                    "role": new_role
                })
                
                with open(json_path_users, "w") as f:
                    json.dump(users,f)

                st.success("Account created!")
                st.rerun()

    st.write("---")
    
elif st.session_state["page"] == "dashboard":
    st.title("💵 Expense Dashboard 💵")

    user_email = st.session_state["user"]["email"]
    user_expenses = []
    for e in expenses:
        if e["email"] == user_email:
            user_expenses.append(e)

    if len(user_expenses) == 0:
        st.info("No expenses found")
        st.stop()
##Calculations
    total_spent = 0

    for e in user_expenses:
        total_spent +=["amount"]

    total_transactions = len(user_expenses)

    if total_transactions >0:
        avg = total_spent / total_transactions
    else:
        avg = 0
    
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
        category_amounts[category] = 0
        
        ##Test this once I add the adding expenses function
