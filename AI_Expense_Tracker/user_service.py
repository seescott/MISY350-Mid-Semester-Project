class UserService:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.users = self.data_manager.load_users()

    def valid_email(self, email):
        return "@" in email and "." in email and len(email) >= 5

    def valid_password(self, password):
        return len(password) >= 5

    def login(self, email, password):
        for user in self.users:
            if user["email"].lower() == email.lower() and user["password"] == password:
                return user
        return None

    def register_user(self, full_name, email, password, role):
        if full_name == "" or email == "" or password == "":
            return False, "Please fill in all fields"

        if not self.valid_email(email):
            return False, "Enter a valid email"

        if not self.valid_password(password):
            return False, "Password must be at least 5 characters"

        for user in self.users:
            if user["email"].lower() == email.lower():
                return False, "Email already exists"

        new_user = {
            "full_name": full_name,
            "email": email,
            "password": password,
            "role": role.lower()
        }

        self.users.append(new_user)
        self.data_manager.save_users(self.users)

        return True, "Account created!"