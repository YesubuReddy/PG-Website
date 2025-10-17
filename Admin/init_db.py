import sqlite3

conn = sqlite3.connect('residents.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS residents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    room_number TEXT NOT NULL,
    room_type TEXT NOT NULL,
    phone TEXT NOT NULL,
    alt_phone TEXT,
    aadhar TEXT NOT NULL,
    join_date TEXT NOT NULL,
    amount_paid REAL NOT NULL,
    due_date TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ Database initialized with alt_phone column.")
