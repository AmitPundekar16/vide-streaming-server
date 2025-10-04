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
