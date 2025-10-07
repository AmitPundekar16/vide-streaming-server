import socket
import tempfile
import vlc
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QMessageBox, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Database.Sqlite_db import get_supabase_name, get_all_videos  # Make sure these functions exist

# ---------- Function to Receive Video from Server ----------
def receive_video(filename, host="127.0.0.1", port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        client_socket.sendall(f"GET {filename}".encode())

        # Receive the first 16 bytes (expected file size)
        raw_size = client_socket.recv(16).decode()
        try:
            file_size = int(raw_size.strip())
        except ValueError:
            print(f"❌ Invalid file size received for '{filename}'")
            return None

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        received = 0
        while received < file_size:
            data = client_socket.recv(4096)
            if not data:
                break
            temp_file.write(data)
            received += len(data)
        temp_file.close()
        return temp_file.name

    except ConnectionRefusedError:
        print("❌ Could not connect to server. Is it running?")
        return None
    except Exception as e:
        print(f"❌ Error receiving video: {e}")
        return None
    finally:
        client_socket.close()


# ---------- Video Player Widget ----------
class VideoPlayer(QWidget):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎬 Video Player")
        self.setGeometry(100, 100, 1000, 600)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.winId()))

        media = self.instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()


# ---------- Dashboard Window ----------
class DashboardWindow(QWidget):
    def __init__(self, host="127.0.0.1", port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.setWindowTitle("A_Server")
        self.setGeometry(100, 50, 1200, 800)  # bigger and centered
        self.setStyleSheet("background-color: #2E3440; color: #ECEFF4;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Project Title
        title = QLabel("A_Server")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #88C0D0;")
        layout.addWidget(title)

        # Video List
        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: #3B4252;
                color: #ECEFF4;
                font-size: 14px;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #88C0D0;
                color: black;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.video_list)

        # Video playback area
        self.video_widget = QWidget()
        self.video_widget.setStyleSheet("background-color: black;")
        layout.addWidget(self.video_widget, stretch=1)

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.video_widget.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_widget.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_widget.winId()))

        # Load video list from DB
        try:
            videos = get_all_videos()  # returns list of tuples: (user_name,)
            if videos:
                for (user_name,) in videos:
                    self.video_list.addItem(user_name)
            else:
                QMessageBox.warning(self, "No Videos", "No videos available in database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load videos from database: {e}")

        # Play on single click
        self.video_list.itemClicked.connect(self.play_video)

    def play_video(self, item):
        user_name = item.text()
        supabase_name = get_supabase_name(user_name)
        if not supabase_name:
            QMessageBox.critical(self, "Error", f"No video found in DB for '{user_name}'.")
            return

        file_path = receive_video(supabase_name, self.host, self.port)
        if not file_path:
            QMessageBox.critical(self, "Error", f"Could not fetch '{supabase_name}' from server.")
            return

        media = self.vlc_instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()


# ---------- Main ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())
