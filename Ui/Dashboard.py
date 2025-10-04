import socket
import tempfile
import vlc
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QMessageBox, QMainWindow, QLabel
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt

# ---------- Video Receiving Function ----------
def receive_video(filename, host="127.0.0.1", port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(f"GET {filename}".encode())

    file_size = int(client_socket.recv(16).decode().strip())
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    received = 0
    while received < file_size:
        data = client_socket.recv(4096)
        if not data:
            break
        temp_file.write(data)
        received += len(data)
    temp_file.close()
    client_socket.close()
    return temp_file.name

# ---------- Request Video List ----------
def request_video_list(host="127.0.0.1", port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(b"LIST")
    data = client_socket.recv(4096).decode()
    client_socket.close()
    return data.split(",") if data else []

# ---------- Video Player ----------
class VideoPlayer(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("🎬 Video Player")
        self.setGeometry(100, 100, 900, 600)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.widget.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.widget.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.widget.winId()))

        media = self.instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()

# ---------- Dashboard Window ----------
class DashboardWindow(QWidget):
    def __init__(self, host="127.0.0.1", port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.setWindowTitle("A_Server Dashboard")
        self.setGeometry(200, 200, 600, 500)
        self.setStyleSheet("background-color: #2E3440; color: #ECEFF4;")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        self.setLayout(layout)

        # ---------- Project Title ----------
        title_label = QLabel("A_Server")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setStyleSheet("color: #88C0D0;")
        layout.addWidget(title_label)

        # ---------- Subtitle ----------
        subtitle_label = QLabel("Available Videos")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 16))
        subtitle_label.setStyleSheet("color: #D8DEE9;")
        layout.addWidget(subtitle_label)

        # ---------- Video List ----------
        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: #3B4252; 
                color: #ECEFF4; 
                font-size: 14px; 
                border: 2px solid #4C566A; 
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #81A1C1;
                color: black;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.video_list)

        # Load videos from server
        try:
            videos = request_video_list(self.host, self.port)
            if videos:
                self.video_list.addItems(videos)
            else:
                QMessageBox.warning(self, "No Videos", "No videos available on server.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not connect to server: {e}")

        # Connect double click
        self.video_list.itemDoubleClicked.connect(self.play_video)

    def play_video(self, item):
        filename = item.text()
        QMessageBox.information(self, "Download", f"Fetching {filename}...")
        try:
            file_path = receive_video(filename, self.host, self.port)
            self.player = VideoPlayer(file_path)
            self.player.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not play video: {e}")
