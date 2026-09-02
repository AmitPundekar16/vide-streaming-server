import socket
import threading
import pickle
import struct
import cv2
from supabase import create_client, Client
import Apikeys

supabase: Client = create_client(Apikeys.SUPABASE_URL, Apikeys.SUPABASE_KEY)

def get_video_bytes(bucket_name, file_name):
    print(f"Trying to fetch '{file_name}' from bucket '{bucket_name}'...")
    try:
        result = supabase.storage.from_(bucket_name).download(file_name)
        print(f"Successfully fetched '{file_name}' ({len(result)} bytes)")
        return result
    except Exception as err:
        print(f"Couldn't fetch '{file_name}' from '{bucket_name}':", err)
        return None

def get_video_list(bucket_name):
    try:
        bucket_items = supabase.storage.from_(bucket_name).list()
        return [f["name"] for f in bucket_items]
    except Exception as err:
        print(f"Error listing videos in bucket '{bucket_name}':", err)
        return []

# ------------------- Client Handler -------------------
def handle_client(client_socket, address):
    print(f"Client connected: {address}")
    try:
        data = client_socket.recv(1024).decode().strip()
        print(f" Request from {address}: {data}")

        # ---------- Live stream request ----------
        if data == "LIVE":
            print(f" Starting live stream for {address}")
            cap = cv2.VideoCapture(0)  # Open webcam
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Serialize frame
                    frame_data = pickle.dumps(frame)
                    message = struct.pack("Q", len(frame_data)) + frame_data
                    client_socket.sendall(message)
            except Exception as e:
                print(f" Live stream error for {address}: {e}")
            finally:
                cap.release()
                client_socket.close()
                print(f"Live stream disconnected: {address}")

        # ---------- Stored video request ----------
        elif data.startswith("GET"):
            parts = data.split(" ", 2)
            if len(parts) < 3:
                client_socket.send(b"ERROR: Missing bucket or file name.")
                return

            _, bucket_name, filename = parts
            print(f" Bucket: '{bucket_name}', File: '{filename}'")

            file_data = get_video_bytes(bucket_name, filename)
            if file_data:
                size_str = str(len(file_data)).encode().ljust(16)
                client_socket.send(size_str)

                chunk_size = 4096
                for i in range(0, len(file_data), chunk_size):
                    client_socket.send(file_data[i:i + chunk_size])
                print(f"✅ Done sending {filename} from bucket {bucket_name}")
            else:
                client_socket.send(b"ERROR: Video not found or failed to download.")

        else:
            client_socket.send(b"ERROR: Invalid request format.")

    except Exception as ex:
        print(f"Exception while handling {address}: {ex}")
    finally:
        if client_socket:
            client_socket.close()
        print(f"Disconnected: {address}")


# ------------------- Start Server -------------------
def start_server(host="0.0.0.0", port=9999):
    print("Starting combined server...")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind((host, port))
    except Exception as e:
        print("Failed to bind socket:", e)
        return

    srv.listen(5)
    print(f"Server running at {host}:{port}")
    print("Waiting for clients...")

    while True:
        sock, addr = srv.accept()
        thread = threading.Thread(target=handle_client, args=(sock, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server() 