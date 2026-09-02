import sqlite3

DB_PATH = "users.db"

# ---------- Connect to DB ----------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()




 

cursor.execute("""
    INSERT INTO videos (name, user_name, bucket_name)
    VALUES (?, ?, ?)
""", ("chandnii.mp4", "The Only Love Of Cricket", "cricket"))
conn.commit()
print("✅ Added new video data.")

cursor.execute("SELECT * FROM videos;")
rows = cursor.fetchall()
print("Current videos table:")
for row in rows:
    print(row)

conn.close()
