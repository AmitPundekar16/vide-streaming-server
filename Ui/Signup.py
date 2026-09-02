import re
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Database.Sqlite_db import register_user  # You need to implement this function
from Ui.Dashboard import DashboardWindow  # Make sure you have Dashboard.py

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

# ---------- Signup Window ----------
class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Up Page")
        self.setGeometry(200, 200, 400, 300)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #2E3440;")  # Dark theme

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 20, 50, 20)
        layout.setSpacing(15)

        # Project Name Label
        project_label = QLabel("A_Server - Sign Up")
        project_label.setAlignment(Qt.AlignCenter)
        project_label.setFont(QFont("Arial", 22, QFont.Bold))
        project_label.setStyleSheet("color: #88C0D0;")
        layout.addWidget(project_label)

        # Email Input
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
        layout.addWidget(self.email_input)

        # Password Input
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
        layout.addWidget(self.password_input)

        # Register Button
        self.register_button = QPushButton("Register")
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #A3BE8C;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #B48EAD;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
        """)
        self.register_button.clicked.connect(self.handle_signup)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    # ---------- Signup Handler ----------
    def handle_signup(self):
        email = self.email_input.text()
        password = self.password_input.text()

        # Validate email
        if not validate_email(email):
            QMessageBox.critical(self, "Invalid Email", "Enter a valid email.")
            return

        # Validate password
        if not validate_password(password):
            QMessageBox.critical(
                self, "Invalid Password",
                "Password must be 8+ chars, include 1 uppercase, 1 number, 1 special symbol."
            )
            return

        # Register user in database
        if register_user(email, password):
            QMessageBox.information(self, "Success", f"User {email} registered successfully!")
            self.close()  # Close signup window

            # Open Dashboard
            self.dashboard = DashboardWindow(email)  # Pass email if needed
            self.dashboard.show()
        else:
            QMessageBox.warning(self, "Error", "Registration failed. User may already exist.")


# ---------- Run Signup Directly (optional) ----------
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = SignupWindow()
    window.show()
    sys.exit(app.exec())
