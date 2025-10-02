from supabase import create_client
import Apikeys  # your config.py with SUPABASE_URL and SUPABASE_KEY

# Create Supabase client
supabase = create_client(Apikeys.SUPABASE_URL, Apikeys.SUPABASE_KEY)

# Attempt to download the video
try:
    files = supabase.storage.from_("Videos").list()  # use your bucket name exactly
    print("Files in bucket:", files)

    video_bytes = supabase.storage.from_("Videos").download("hitman.mp4")
    print("✅ Video fetched successfully!")
    print("Video size (bytes):", len(video_bytes))
except Exception as e:
    print("❌ Error fetching video:", e)
