import re
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Database.Sqlite_db import check_user, register_user  

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    ok = re.match(pattern, email) is not None
    return ok


def validate_password(pw):
  
    if len(pw) < 8:
        return False
    if not re.search(r"[A-Z]", pw):
        return False
    if not re.search(r"[0-9]", pw):
        return False
    if not re.search(r"[@$!%*?&#]", pw):
        return False
    return True


# -------------- Authentication Window --------------
class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A_Server Authentication")
        self.setGeometry(200, 200, 400, 320)
        self.setFixedSize(400, 320)
        self.setStyleSheet("background-color: #2E3440;") 

        self.handle_success = None  

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 20, 50, 20)
        layout.setSpacing(15)

        title_label = QLabel("A_Server")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 26, QFont.Bold))
        title_label.setStyleSheet("color: #88C0D0;")
        layout.addWidget(title_label)

        self.email_field = QLineEdit()
        self.email_field.setPlaceholderText("Enter your email")
        self.email_field.setStyleSheet("""
            QLineEdit {
                padding: 5px; border: 2px solid #4C566A;
                border-radius: 8px; background: #3B4252; color: #ECEFF4;
            }
            QLineEdit:focus { border: 2px solid #81A1C1; }
        """)
        layout.addWidget(self.email_field)

        self.pass_field = QLineEdit()
        self.pass_field.setPlaceholderText("Enter your password")
        self.pass_field.setEchoMode(QLineEdit.Password)
        self.pass_field.setStyleSheet("""
            QLineEdit {
                padding: 5px; border: 2px solid #4C566A;
                border-radius: 8px; background: #3B4252; color: #ECEFF4;
            }
            QLineEdit:focus { border: 2px solid #81A1C1; }
        """)
        layout.addWidget(self.pass_field)

        self.btn_login = QPushButton("Login")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC; color: white; font-weight: bold;
                padding: 8px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #81A1C1; }
            QPushButton:pressed { background-color: #4C566A; }
        """)
        self.btn_login.clicked.connect(self.handle_login_clicked)
        layout.addWidget(self.btn_login)

        self.btn_signup = QPushButton("Sign Up")
        self.btn_signup.setCursor(Qt.PointingHandCursor)
        self.btn_signup.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C; color: white; font-weight: bold;
                padding: 8px; border-radius: 10px;
            }
            QPushButton:hover { background-color: #B48EAD; }
            QPushButton:pressed { background-color: #4C566A; }
        """)
        self.btn_signup.clicked.connect(self.handle_signup_clicked)
        layout.addWidget(self.btn_signup)

        self.setLayout(layout)

    def handle_login_clicked(self):
        email = self.email_field.text().strip()
        pw = self.pass_field.text()

        if not validate_email(email):
            QMessageBox.critical(self, "Invalid Email", "Please enter a proper email address.")
            return
        if not validate_password(pw):
            QMessageBox.critical(self, "Weak Password",
                                 "Password must be 8+ chars, include 1 uppercase, 1 number, and 1 special character.")
            return

        try:
            ok = check_user(email, pw)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Something went wrong while checking user:\n{e}")
            return

        if ok:
            QMessageBox.information(self, "Welcome!", f"Successfully logged in as {email}")
            if self.handle_success:
                self.handle_success(email)
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Email or password seems incorrect.")

    def handle_signup_clicked(self):
        email = self.email_field.text().strip()
        pw = self.pass_field.text()

        if not validate_email(email):
            QMessageBox.critical(self, "Invalid Email", "Please enter a valid email address.")
            return
        if not validate_password(pw):
            QMessageBox.critical(self, "Weak Password",
                                 "Password must be 8+ chars, include 1 uppercase, 1 number, and 1 special character.")
            return

        try:
            created = register_user(email, pw)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong during registration:\n{e}")
            return

        if created:
            QMessageBox.information(self, "Success", f"Account created for {email}!")
            if self.handle_success:
                self.handle_success(email)
            self.close()
        else:
            QMessageBox.warning(self, "Registration Failed", "User may already exist or DB error occurred.")
