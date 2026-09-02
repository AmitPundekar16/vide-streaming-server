import socket
import cv2
import pickle
import struct

HOST = '127.0.0.1'  # Same as dashboard host
PORT = 9999

# Create TCP server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Live server listening on {HOST}:{PORT}")

conn, addr = server_socket.accept()
print("Client connected from:", addr)

# Open webcam
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Serialize frame
        data = pickle.dumps(frame)
        # Pack message size first
        message = struct.pack("Q", len(data)) + data
        conn.sendall(message)
finally:
    cap.release()
    conn.close()
    server_socket.close()
