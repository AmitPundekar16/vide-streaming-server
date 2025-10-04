import re
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Database.Sqlite_db import check_user  # Make sure Database folder has __init__.py

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

# ---------- Login Window ----------
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Page")
        self.setGeometry(200, 200, 400, 250)
        self.setFixedSize(400, 250)
        self.setStyleSheet("background-color: #2E3440;")  # Dark background

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 20, 50, 20)
        layout.setSpacing(15)

        # Project Name Label
        project_label = QLabel("A_Server")
        project_label.setAlignment(Qt.AlignCenter)
        project_label.setFont(QFont("Arial", 26, QFont.Bold))
        project_label.setStyleSheet("color: #88C0D0;")
        layout.addWidget(project_label)

        # Email Input
        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet("color: #D8DEE9; font-weight: bold;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #4C566A;
                border-radius: 8px;
                background: #3B4252;
                color: #ECEFF4;
            }
            QLineEdit:focus {
                border: 2px solid #81A1C1;
            }
        """)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        # Password Input
        self.password_label = QLabel("Password:")
        self.password_label.setStyleSheet("color: #D8DEE9; font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #4C566A;
                border-radius: 8px;
                background: #3B4252;
                color: #ECEFF4;
            }
            QLineEdit:focus {
                border: 2px solid #81A1C1;
            }
        """)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #5E81AC;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    # ---------- Login Handler ----------
    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not validate_email(email):
            QMessageBox.critical(self, "Invalid Email", "Enter a valid email.")
            return

        if not validate_password(password):
            QMessageBox.critical(
                self, "Invalid Password",
                "Password must be 8+ chars, include 1 uppercase, 1 number, 1 special symbol."
            )
            return

        if check_user(email, password):
            QMessageBox.information(self, "Login Success", f"Welcome, {email}!")
            self.close()  # close login window after success
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect email or password.")

# ---------- Run the App ----------
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
