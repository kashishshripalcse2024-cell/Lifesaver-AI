import sqlite3

conn = sqlite3.connect("tasks.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    date TEXT,
    priority TEXT,
    completed INTEGER DEFAULT 0
)
""")

try:
    cursor.execute("ALTER TABLE tasks ADD COLUMN completed INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass

conn.commit()
conn.close()

print("Database updated successfully!")