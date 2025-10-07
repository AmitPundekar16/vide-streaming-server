import socket
from supabase import create_client, Client
import Apikeys  # contains SUPABASE_URL and SUPABASE_KEY
import threading

# ---------- Supabase Setup ----------
supabase: Client = create_client(Apikeys.SUPABASE_URL, Apikeys.SUPABASE_KEY)
BUCKET_NAME = "A_Server"





def get_video_list():
    print(f"🪣 Checking bucket: {BUCKET_NAME}")
    try:
        # Debug 1: List buckets
        buckets = supabase.storage.list_buckets()
        print("📦 Buckets available:", [b['name'] for b in buckets])

        # Debug 2: List objects in bucket
        result = supabase.storage.from_(BUCKET_NAME).list()
        print("🧾 Raw Supabase list() response:", result)

        if not result:
            print("⚠️ No files found. Bucket may be private or name mismatch.")
        else:
            print("✅ Files found:", [f["name"] for f in result])

        return [f["name"] for f in result]
    except Exception as e:
        print("❌ Exception while listing videos:", e)
        return []



def get_video_bytes(file_name):
    """
    Fetch the requested video as bytes from Supabase.
    """
    try:
        print(f"🎥 Fetching '{file_name}' from Supabase...")
        response = supabase.storage.from_(BUCKET_NAME).download(file_name)
        print(f"✅ Video '{file_name}' fetched ({len(response)} bytes)")
        return response
    except Exception as e:
        print(f"❌ Error fetching video '{file_name}':", e)
        return None


# ---------- Client Handler ----------
def handle_client(client_socket, address):
    print(f"🔗 Client connected: {address}")
    try:
        # Receive request (LIST or GET <filename>)
        request = client_socket.recv(1024).decode().strip()
        print(f"📩 Request from {address}: {request}")

        if request == "LIST":
            # Send list of available videos
            videos = get_video_list()
            client_socket.send(",".join(videos).encode())

        elif request.startswith("GET"):
            # Extract filename
            _, file_name = request.split(" ", 1)
            video_bytes = get_video_bytes(file_name)

            if video_bytes:
                # Send file size first
                client_socket.send(str(len(video_bytes)).encode().ljust(16))

                # Send in chunks
                chunk_size = 4096
                for i in range(0, len(video_bytes), chunk_size):
                    client_socket.send(video_bytes[i:i + chunk_size])

                print(f"✅ Finished sending {file_name}")
            else:
                client_socket.send(b"ERROR: Video not found or failed to fetch.")

        else:
            client_socket.send(b"ERROR: Invalid request.")

    except Exception as e:
        print(f"❌ Error handling client {address}: {e}")

    finally:
        client_socket.close()
        print(f"🔒 Disconnected: {address}")


# ---------- Main Server ----------
def start_server(host="0.0.0.0", port=9999):
    """
    Start the Supabase video streaming server.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"🚀 Server started on {host}:{port}")
    print("💡 Waiting for client requests...")

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
