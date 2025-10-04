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

# ---------- Insert User ----------
def insert_user(email, password):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        print("User added successfully!")

    except sqlite3.IntegrityError:
        print("Error: Email already exists!")
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
        print("Login successful!")
        return True
    else:
        print("Invalid email or password.")
        return False





