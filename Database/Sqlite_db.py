import sqlite3

# ---------- Create Database and Table ----------
def create_table():
    conn = sqlite3.connect("users.db")  # creates users.db file
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

 # Create videos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            name TEXT PRIMARY KEY,          -- Supabase video file name
            user_name TEXT NOT NULL         -- User-defined display name
        )
    """)

    conn.commit()
    conn.close()

# ---------- Video Functions ----------
def add_video(name, user_name):
    """Insert a new video into the videos table."""
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO videos (name, user_name) VALUES (?, ?)", (name, user_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Video '{name}' already exists!")
        return False
    finally:
        conn.close()


def get_supabase_name(user_name):
    """Return the Supabase file name for a given user_name"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM videos WHERE user_name = ?", (user_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_videos():
    """Return a list of tuples (name, user_name) for all videos."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_name FROM videos")
    result = cursor.fetchall()
    conn.close()
    return result

    conn.commit()
    conn.close()

# ---------- Insert User / Register ----------
def register_user(email, password):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True  # registration successful
    except sqlite3.IntegrityError:
        print("Error: Email already exists!")
        return False
    finally:
        conn.close()

# ---------- Retrieve User (Login Check) ----------
def check_user(email, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        return True
    else:
        return False

# ---------- Ensure table exists when module is imported ----------
create_table()
