import socket
import tempfile
import vlc
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QMessageBox, QLabel, QPushButton
)
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient
from PyQt5.QtCore import Qt
from Database.Sqlite_db import get_supabase_name, get_all_videos
from Ui.Searchbar import SearchBar


# ---------- Video Receiving ----------
def receive_video(filename, bucket_name, host="127.0.0.1", port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        client_socket.sendall(f"GET {bucket_name} {filename}".encode())

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

    except Exception as e:
        print(f"❌ Error receiving video: {e}")
        return None
    finally:
        client_socket.close()


# ---------- Dashboard ----------
class DashboardWindow(QWidget):
    def __init__(self, host="127.0.0.1", port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.current_bucket = None

        # ---------- Window setup ----------
        self.setWindowTitle("🎬 A_Server Video Player")
        self.setGeometry(200, 100, 950, 650)

        # ---------- Background (modern, soft gradient) ----------
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 600)
        gradient.setColorAt(0, QColor("#E3F2FD"))  # very light blue
        gradient.setColorAt(1, QColor("#BBDEFB"))  # fresh sky blue
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # ---------- Main layout ----------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(12)
        self.setLayout(main_layout)

        # ---------- Title ----------
        title = QLabel("A_Server Dashboard")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0D47A1; margin-bottom: 6px;")
        main_layout.addWidget(title)

        # ---------- Search Bar ----------
        self.search_bar = SearchBar(search_callback=self.handle_search)
        main_layout.addWidget(self.search_bar)

        # ---------- Video List ----------
        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                color: #333;
                border-radius: 8px;
                font-size: 14px;
                padding: 6px;
                border: 1px solid #90CAF9;
            }
            QListWidget::item:selected {
                background-color: #42A5F5;
                color: white;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.video_list, 0)

        # ---------- Video Display Area ----------
        self.video_widget = QWidget()
        self.video_widget.setStyleSheet("""
            background-color: black;
            border-radius: 10px;
            border: 2px solid #1976D2;
        """)
        main_layout.addWidget(self.video_widget, 1)

        # ---------- Control Buttons ----------
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        controls_layout.setAlignment(Qt.AlignCenter)

        button_style = """
            QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 8px;
                padding: 7px 15px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
        """

        self.back_btn = QPushButton("⏪ Back 10s")
        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")
        self.stop_btn = QPushButton("⏹ Stop")
        self.forward_btn = QPushButton("⏩ Forward 10s")

        for btn in [self.back_btn, self.play_btn, self.pause_btn, self.stop_btn, self.forward_btn]:
            btn.setStyleSheet(button_style)
            controls_layout.addWidget(btn)

        main_layout.addLayout(controls_layout)

        # ---------- VLC Setup ----------
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.video_widget.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_widget.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_widget.winId()))

        # ---------- Connect Buttons ----------
        self.video_list.itemClicked.connect(self.play_video)
        self.play_btn.clicked.connect(self.play_video_action)
        self.pause_btn.clicked.connect(self.pause_video)
        self.stop_btn.clicked.connect(self.stop_video)
        self.back_btn.clicked.connect(lambda: self.seek_video(-10))
        self.forward_btn.clicked.connect(lambda: self.seek_video(10))

    # ---------- Load Videos ----------
    def load_videos(self, bucket=None):
        self.video_list.clear()
        self.current_bucket = bucket
        try:
            videos = get_all_videos(bucket=bucket)
            if videos:
                for (user_name,) in videos:
                    self.video_list.addItem(user_name)
            else:
                self.video_list.addItem("No videos found 😢")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load videos: {e}")

    # ---------- Handle Search ----------
    def handle_search(self, bucket_name):
        self.load_videos(bucket=bucket_name)

    # ---------- Play Video ----------
    def play_video(self, item):
        user_name = item.text()
        if "No videos" in user_name:
            return

        supabase_name = get_supabase_name(user_name, bucket_name=self.current_bucket)
        if not supabase_name:
            QMessageBox.critical(
                self, "Error",
                f"No video found for '{user_name}' in bucket '{self.current_bucket}'"
            )
            return

        file_path = receive_video(supabase_name, self.current_bucket, self.host, self.port)
        if not file_path:
            QMessageBox.critical(self, "Error", f"Could not fetch '{supabase_name}' from server.")
            return

        media = self.vlc_instance.media_new(file_path)
        self.player.set_media(media)

        # 🎯 Play video inside the same widget size (fit, not stretch)
        self.player.video_set_scale(0)
        self.player.video_set_aspect_ratio(None)

        self.player.play()

    # ---------- Control Actions ----------
    def play_video_action(self):
        self.player.play()

    def pause_video(self):
        self.player.pause()

    def stop_video(self):
        self.player.stop()

    def seek_video(self, seconds):
        length = self.player.get_length()
        current = self.player.get_time()
        new_time = max(0, min(current + (seconds * 1000), length))
        self.player.set_time(int(new_time))


# ---------- Run App ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())
