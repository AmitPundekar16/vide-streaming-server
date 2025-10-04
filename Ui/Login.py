import re
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Database.Sqlite_db import check_user, register_user  # Make sure you implement register_user

# ---------- Validation Functions ----------
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[@$!%*?&#]", password):
        return False
    return True

# ---------- Main Window ----------
class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A_Server Authentication")
        self.setGeometry(200, 200, 400, 320)
        self.setFixedSize(400, 320)
        self.setStyleSheet("background-color: #2E3440;")

        # Callback for successful login/signup
        self.handle_success = None  # client.py will assign this

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 20, 50, 20)
        layout.setSpacing(15)

        # Project Name
        project_label = QLabel("A_Server")
        project_label.setAlignment(Qt.AlignCenter)
        project_label.setFont(QFont("Arial", 26, QFont.Bold))
        project_label.setStyleSheet("color: #88C0D0;")
        layout.addWidget(project_label)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 5px; border: 2px solid #4C566A;
                border-radius: 8px; background: #3B4252; color: #ECEFF4;
            }
            QLineEdit:focus { border: 2px solid #81A1C1; }
        """)
        layout.addWidget(self.email_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit { padding: 5px; border: 2px solid #4C566A;
            border-radius: 8px; background: #3B4252; color: #ECEFF4; }
            QLineEdit:focus { border: 2px solid #81A1C1; }
        """)
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC; color: white; font-weight: bold;
                padding: 8px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #81A1C1; }
            QPushButton:pressed { background-color: #4C566A; }
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Signup Button
        self.signup_button = QPushButton("Sign Up")
        self.signup_button.setCursor(Qt.PointingHandCursor)
        self.signup_button.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C; color: white; font-weight: bold;
                padding: 8px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #B48EAD; }
            QPushButton:pressed { background-color: #4C566A; }
        """)
        self.signup_button.clicked.connect(self.handle_signup)
        layout.addWidget(self.signup_button)

        self.setLayout(layout)

    # ---------- Login ----------
    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not validate_email(email):
            QMessageBox.critical(self, "Invalid Email", "Enter a valid email.")
            return
        if not validate_password(password):
            QMessageBox.critical(self, "Invalid Password",
                                 "Password must be 8+ chars, include 1 uppercase, 1 number, 1 special symbol.")
            return

        if check_user(email, password):
            QMessageBox.information(self, "Login Success", f"Login successful! Welcome, {email}")
            if self.handle_success:
                self.handle_success(email)  # return control to client.py
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect email or password.")

    # ---------- Signup ----------
    def handle_signup(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not validate_email(email):
            QMessageBox.critical(self, "Invalid Email", "Enter a valid email.")
            return
        if not validate_password(password):
            QMessageBox.critical(self, "Invalid Password",
                                 "Password must be 8+ chars, include 1 uppercase, 1 number, 1 special symbol.")
            return

        if register_user(email, password):
            QMessageBox.information(self, "Registration Success", f"User {email} registered successfully!")
            if self.handle_success:
                self.handle_success(email)  # return control to client.py
            self.close()
        else:
            QMessageBox.warning(self, "Registration Failed", "User may already exist.")
