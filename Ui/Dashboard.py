import socket
import tempfile
import vlc
import sys
import threading
import pickle
import struct
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QMessageBox, QLabel, QPushButton
)
from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient, QImage, QPixmap
from PyQt5.QtCore import Qt
from Database.Sqlite_db import get_supabase_name, get_all_videos
from Ui.Searchbar import SearchBar

# ------------------- Video Receiving Function -------------------
def receive_video(filename, bucket_name, host="127.0.0.1", port=9999):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        client_socket.sendall(f"GET {bucket_name} {filename}".encode())

        raw_size = client_socket.recv(16).decode()
        try:
            file_size = int(raw_size.strip())
        except ValueError:
            print(f"Invalid file size received for '{filename}'")
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
        print(f"Error receiving video: {e}")
        return None
    finally:
        client_socket.close()

# ------------------- Full Screen Window -------------------
class FullScreenWindow(QWidget):
    def __init__(self, media_path=None, is_live=False, host="127.0.0.1", port=9999, zoom_factor=1.0):
        super().__init__()
        self.media_path = media_path
        self.is_live = is_live
        self.host = host
        self.port = port
        self.zoom_factor = zoom_factor
        self.live_streaming = False

        self.setWindowTitle("Full Screen Player")
        self.showFullScreen()

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # Video area
        self.video_widget = QWidget()
        self.video_widget.setStyleSheet("background-color:black;")
        self.layout.addWidget(self.video_widget, 1)

        # Live label for live streaming
        if self.is_live:
            self.live_label = QLabel(self.video_widget)
            self.live_label.setAlignment(Qt.AlignCenter)
            self.live_label.setGeometry(0,0,self.video_widget.width(), self.video_widget.height())
            self.live_label.setStyleSheet("background-color:black;")
            self.live_label.setScaledContents(True)

        # Controls at bottom
        self.controls_widget = QWidget()
        self.controls_widget.setStyleSheet("background-color: rgba(0,0,0,0.6);")
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(12)
        self.controls_layout.setAlignment(Qt.AlignCenter)
        self.controls_widget.setLayout(self.controls_layout)
        self.layout.addWidget(self.controls_widget)

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

        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")
        self.stop_btn = QPushButton("⏹ Stop")
        self.zoom_in_btn = QPushButton("🔍 Zoom In")
        self.zoom_out_btn = QPushButton("🔍 Zoom Out")
        self.exit_btn = QPushButton("❌ Exit Full Screen")

        for btn in [self.play_btn, self.pause_btn, self.stop_btn,
                    self.zoom_in_btn, self.zoom_out_btn, self.exit_btn]:
            btn.setStyleSheet(button_style)
            self.controls_layout.addWidget(btn)

        # VLC for stored video
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        if not self.is_live and self.media_path:
            media = self.vlc_instance.media_new(self.media_path)
            self.player.set_media(media)

        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.video_widget.winId())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_widget.winId())
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_widget.winId()))

        # Connect buttons
        self.play_btn.clicked.connect(self.play_video)
        self.pause_btn.clicked.connect(self.pause_video)
        self.stop_btn.clicked.connect(self.stop_video)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.exit_btn.clicked.connect(self.exit_fullscreen)

        # Start playback
        if self.is_live:
            self.live_streaming = True
            threading.Thread(target=self._live_stream_thread, daemon=True).start()
        else:
            self.player.play()
            self.player.video_set_scale(self.zoom_factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'live_label'):
            self.live_label.setGeometry(0,0,self.video_widget.width(), self.video_widget.height())

    # ---------------- Video Controls ----------------
    def play_video(self):
        if self.is_live:
            self.live_streaming = True
        else:
            self.player.play()
            self.player.video_set_scale(self.zoom_factor)

    def pause_video(self):
        if self.is_live:
            self.live_streaming = False
        else:
            self.player.pause()

    def stop_video(self):
        if self.is_live:
            self.live_streaming = False
            if hasattr(self, 'live_label'):
                self.live_label.clear()
        else:
            self.player.stop()

    def zoom_in(self):
        self.zoom_factor += 0.1
        if not self.is_live:
            self.player.video_set_scale(self.zoom_factor)

    def zoom_out(self):
        self.zoom_factor = max(0.1, self.zoom_factor - 0.1)
        if not self.is_live:
            self.player.video_set_scale(self.zoom_factor)

    def exit_fullscreen(self):
        self.live_streaming = False
        self.player.stop()
        self.close()

    # ---------------- Live Stream ----------------
    def _live_stream_thread(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            client_socket.sendall(b"LIVE")
            data = b""
            payload_size = struct.calcsize("Q")

            while self.live_streaming:
                while len(data) < payload_size:
                    packet = client_socket.recv(4096)
                    if not packet:
                        return
                    data += packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]
                frame = pickle.loads(frame_data)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                scaled_width = int(pixmap.width() * self.zoom_factor)
                scaled_height = int(pixmap.height() * self.zoom_factor)
                pixmap = pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                if hasattr(self, 'live_label'):
                    self.live_label.setPixmap(pixmap)
                    self.live_label.setAlignment(Qt.AlignCenter)
        except Exception as e:
            print(f"Live stream error: {e}")
        finally:
            client_socket.close()
            self.live_streaming = False

# ------------------- Main Dashboard Window -------------------
class DashboardWindow(QWidget):
    def __init__(self, host="127.0.0.1", port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.current_bucket = None
        self.zoom_factor = 1.0
        self.live_streaming = False

        self.setWindowTitle("A_Server Video Player")
        self.setGeometry(200, 100, 1000, 700)

        # Gradient background
        palette = QPalette()
        gradient = QLinearGradient(0,0,0,700)
        gradient.setColorAt(0, QColor("#E3F2FD"))
        gradient.setColorAt(1, QColor("#BBDEFB"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # Layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Title
        self.title = QLabel("A_Server Dashboard")
        self.title.setFont(QFont("Segoe UI",20,QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("color:#0D47A1;margin-bottom:6px;")
        self.main_layout.addWidget(self.title)

        # Search bar
        self.search_bar = SearchBar(search_callback=self.handle_search)
        self.main_layout.addWidget(self.search_bar)

        # Horizontal layout
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Video list
        self.video_list = QListWidget()
        self.video_list.setFixedWidth(250)
        self.content_layout.addWidget(self.video_list)

        # Video display
        self.video_widget = QLabel()
        self.video_widget.setAlignment(Qt.AlignCenter)
        self.video_widget.setStyleSheet("background-color:black; border:2px solid #1976D2;")
        self.video_widget.setMinimumSize(700,400)
        self.video_widget.setMaximumSize(800,450)
        self.video_widget.setScaledContents(True)
        self.content_layout.addWidget(self.video_widget)

        # Controls
        self.controls_layout = QHBoxLayout()
        self.main_layout.addLayout(self.controls_layout)

        # Buttons
        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")
        self.stop_btn = QPushButton("⏹ Stop")
        self.zoom_in_btn = QPushButton("🔍 Zoom In")
        self.zoom_out_btn = QPushButton("🔍 Zoom Out")
        self.fullscreen_btn = QPushButton("⛶ Full Screen")
        self.live_btn = QPushButton("🔴 Live Stream")
        self.controls = [self.play_btn,self.pause_btn,self.stop_btn,
                         self.zoom_in_btn,self.zoom_out_btn,self.fullscreen_btn,self.live_btn]

        for btn in self.controls:
            btn.setStyleSheet("background-color:#1976D2;color:white;border-radius:8px;padding:7px 15px;font-weight:600;")
            self.controls_layout.addWidget(btn)

        # VLC
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.video_widget.winId())
        elif sys.platform=="win32":
            self.player.set_hwnd(self.video_widget.winId())
        elif sys.platform=="darwin":
            self.player.set_nsobject(int(self.video_widget.winId()))

        # Connections
        self.video_list.itemClicked.connect(self.play_video)
        self.play_btn.clicked.connect(self.play_video_action)
        self.pause_btn.clicked.connect(self.pause_video)
        self.stop_btn.clicked.connect(self.stop_video)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.fullscreen_btn.clicked.connect(self.open_fullscreen)
        self.live_btn.clicked.connect(self.open_live_fullscreen)

    # ---------- Video List ----------
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
            QMessageBox.critical(self,"Error",f"Could not load videos: {e}")

    def handle_search(self,bucket_name):
        self.load_videos(bucket=bucket_name)

    # ---------- Stored Video ----------
    def play_video(self,item):
        user_name = item.text()
        if "No videos" in user_name:
            return
        supabase_name = get_supabase_name(user_name, bucket_name=self.current_bucket)
        if not supabase_name:
            QMessageBox.critical(self,"Error",f"No video found for '{user_name}'")
            return
        file_path = receive_video(supabase_name, self.current_bucket, self.host, self.port)
        if not file_path:
            QMessageBox.critical(self,"Error",f"Could not fetch '{supabase_name}' from server.")
            return
        media = self.vlc_instance.media_new(file_path)
        self.player.set_media(media)
        self.player.video_set_scale(self.zoom_factor)
        self.player.video_set_aspect_ratio(None)
        self.player.play()

    def play_video_action(self):
        self.player.play()
        self.player.video_set_scale(self.zoom_factor)

    def pause_video(self):
        self.player.pause()

    def stop_video(self):
        self.player.stop()

    def zoom_in(self):
        self.zoom_factor +=0.1
        self.player.video_set_scale(self.zoom_factor)

    def zoom_out(self):
        self.zoom_factor = max(0.1,self.zoom_factor-0.1)
        self.player.video_set_scale(self.zoom_factor)

    def open_fullscreen(self):
        media_path = None
        if self.player.get_media():
            media_path = self.player.get_media().get_mrl().replace("file:///","")
        self.fullscreen_window = FullScreenWindow(media_path=media_path,is_live=False,
                                                  host=self.host, port=self.port, zoom_factor=self.zoom_factor)
        self.fullscreen_window.show()

    def open_live_fullscreen(self):
        self.fullscreen_window = FullScreenWindow(media_path=None,is_live=True,
                                                  host=self.host, port=self.port, zoom_factor=self.zoom_factor)
        self.fullscreen_window.show()

# ------------------- Run -------------------
if __name__=="__main__":
    app = QApplication(sys.argv)
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec_())
