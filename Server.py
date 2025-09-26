import socket
import os

VIDEO_FILE = "hitman.mp4"

def start_server(host="0.0.0.0", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Client connected: {addr}")

        if os.path.exists(VIDEO_FILE):
            filesize = os.path.getsize(VIDEO_FILE)

            # Send file size first
            client_socket.send(str(filesize).encode() + b"\n")

            # Send video in chunks
            with open(VIDEO_FILE, "rb") as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    client_socket.send(chunk)

            print("Video sent successfully.")
        else:
            client_socket.send(b"ERROR: Video not found")

        client_socket.close()

if __name__ == "__main__":
    start_server()
