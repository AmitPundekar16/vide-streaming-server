import socket
from supabase import create_client, Client
import Apikeys  # import your secrets

# Create Supabase client
supabase: Client = create_client(Apikeys.SUPABASE_URL, Apikeys.SUPABASE_KEY)

def get_video_bytes(file_name):
    """
    Fetch video from Supabase bucket as raw bytes.
    """
    response = supabase.storage.from_("Videos").download(file_name)
    return response  # raw bytes

def start_server(host="0.0.0.0", port=9999, video_name="hitman.mp4"):
    """
    Start the video streaming server.
    """
    # Fetch video from Supabase
    print(f"🎥 Fetching '{video_name}' from Supabase...")
    video_bytes = get_video_bytes(video_name)
    print(f"✅ Video fetched ({len(video_bytes)} bytes)")

    # Setup socket server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"🚀 Server started at {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"🔗 Client connected: {addr}")

        # Send file size first (fixed 16-byte header)
        client_socket.send(str(len(video_bytes)).encode().ljust(16))

        # Send video in chunks
        chunk_size = 4096
        for i in range(0, len(video_bytes), chunk_size):
            client_socket.send(video_bytes[i:i+chunk_size])

        client_socket.close()
        print("✅ Video sent and client disconnected")

if __name__ == "__main__":
    start_server(video_name="hitman.mp4")
