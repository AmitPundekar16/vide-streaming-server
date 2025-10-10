import socket
import threading
from supabase import create_client, Client
import Apikeys

# Supabase client
supabase: Client = create_client(Apikeys.SUPABASE_URL, Apikeys.SUPABASE_KEY)


# ---------- Get video bytes ----------
def get_video_bytes(bucket_name, file_name):
    print(f"🎥 Trying to fetch '{file_name}' from bucket '{bucket_name}'...")
    try:
        result = supabase.storage.from_(bucket_name).download(file_name)
        print(f"✅ Successfully fetched '{file_name}' ({len(result)} bytes)")
        return result
    except Exception as err:
        print(f"❌ Couldn't fetch '{file_name}' from '{bucket_name}':", err)
        return None


# ---------- Get list of videos ----------
def get_video_list(bucket_name):
    try:
        bucket_items = supabase.storage.from_(bucket_name).list()
        return [f["name"] for f in bucket_items]
    except Exception as err:
        print(f"❌ Error listing videos in bucket '{bucket_name}':", err)
        return []


# ---------- Handle client ----------
def handle_client(client_socket, address):
    print(f"🔗 Client connected: {address}")
    try:
        data = client_socket.recv(1024).decode().strip()
        print(f"📩 Request from {address}: {data}")

        if data.startswith("GET"):
            parts = data.split(" ", 2)  # Split into 3 parts: GET, bucket, filename
            if len(parts) < 3:
                client_socket.send(b"ERROR: Missing bucket or file name.")
                return

            _, bucket_name, filename = parts
            print(f"🪣 Bucket received from client: '{bucket_name}'")
            print(f"🎥 File requested: '{filename}'")

            file_data = get_video_bytes(bucket_name, filename)  # Modify this function to accept bucket_name

            if file_data:
                size_str = str(len(file_data)).encode().ljust(16)
                client_socket.send(size_str)

                chunk_size = 4096
                for i in range(0, len(file_data), chunk_size):
                    client_socket.send(file_data[i:i + chunk_size])
                print(f"✅ Done sending {filename} from bucket {bucket_name}")
            else:
                client_socket.send(b"ERROR: Video not found or failed to download.")

        elif data == "LIST":
            # Optional: list videos for a specific bucket
            client_socket.send(b"ERROR: LIST not implemented with bucket.")
        else:
            client_socket.send(b"ERROR: Invalid request format.")

    except Exception as ex:
        print(f"❌ Exception while handling {address}: {ex}")
    finally:
        client_socket.close()
        print(f"🔒 Disconnected: {address}")


# ---------- Start server ----------
def start_server(host="0.0.0.0", port=9999):
    print("🧠 Starting server...")
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        srv.bind((host, port))
    except Exception as e:
        print("❌ Failed to bind socket:", e)
        return

    srv.listen(5)
    print(f"🚀 Server running at {host}:{port}")
    print("💡 Waiting for clients...")

    while True:
        sock, addr = srv.accept()
        thread = threading.Thread(target=handle_client, args=(sock, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server()
