import sys
import socket
import tempfile
import vlc
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

def receive_video(host="127.0.0.1", port=9999):
    """
    Connect to the server and receive video file.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Receive file size (first 16 bytes)
    file_size = int(client_socket.recv(16).decode().strip())

    # Save to a temporary file
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
    return temp_file.name  # return path of temp file

class VideoPlayer(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("🎬 Video Streaming Client")
        self.setGeometry(100, 100, 900, 600)

        # VLC instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Video frame widget
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        # Embed VLC video output into PyQt5 widget
        if sys.platform.startswith("linux"):  # for Linux
            self.player.set_xwindow(self.widget.winId())
        elif sys.platform == "win32":  # for Windows
            self.player.set_hwnd(self.widget.winId())
        elif sys.platform == "darwin":  # for macOS
            self.player.set_nsobject(int(self.widget.winId()))

        # Load and play media
        media = self.instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()

if __name__ == "__main__":
    print("📡 Connecting to server...")
    file_path = receive_video()
    print("✅ Video received, starting playback...")

    app = QApplication(sys.argv)
    player = VideoPlayer(file_path)
    player.show()
    sys.exit(app.exec_())
