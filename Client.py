import sys
from PyQt5.QtWidgets import QApplication
from Ui.Login import AuthWindow
from Ui.Dashboard import DashboardWindow
from Database.Sqlite_db import create_table

if __name__ == "__main__":
    create_table()
    app = QApplication(sys.argv)

    login_window = AuthWindow()

    def on_login_success(user_email):
        login_window.dashboard = DashboardWindow()  
        login_window.dashboard.show()
        login_window.close()  

    login_window.handle_success = on_login_success
    login_window.show()

    sys.exit(app.exec_())
