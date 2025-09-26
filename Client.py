import sys
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from threading import Thread

SERVER_IP = "127.0.0.1"
PORT = 5000
OUTPUT_FILE = "received.mp4"

def download_video():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    filesize = int(client_socket.recv(1024).decode().strip())
    print(f"Receiving video of size {filesize} bytes...")

    received_data = b""
    while len(received_data) < filesize:
        packet = client_socket.recv(1024)
        if not packet:
            break
        received_data += packet

    with open(OUTPUT_FILE, "wb") as f:
        f.write(received_data)

    print("Video received and saved as", OUTPUT_FILE)
    client_socket.close()
    return OUTPUT_FILE

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Video Streaming Client")
        self.setGeometry(200, 100, 800, 600)

        layout = QVBoxLayout()

        self.label = QLabel("Python Video Streaming (PyQt5)", self)
        layout.addWidget(self.label)

        # Video widget
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        # Buttons
        self.download_btn = QPushButton("Download Video from Server")
        self.download_btn.clicked.connect(self.download_video_thread)
        layout.addWidget(self.download_btn)

        self.play_btn = QPushButton("Play Downloaded Video")
        self.play_btn.clicked.connect(self.play_video)
        layout.addWidget(self.play_btn)

        self.setLayout(layout)

        # Media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

    def download_video_thread(self):
        Thread(target=self._download_video).start()

    def _download_video(self):
        path = download_video()
        self.label.setText(f"Downloaded: {path}")

    def play_video(self):
        url = QUrl.fromLocalFile(OUTPUT_FILE)
        self.media_player.setMedia(QMediaContent(url))
        self.media_player.play()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
