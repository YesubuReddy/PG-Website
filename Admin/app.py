from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_NAME = "residents.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
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

# ---------- API Endpoints ----------

@app.route("/api/room_types", methods=["GET"])
def get_room_types():
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT room_type FROM residents ORDER BY room_type").fetchall()
    conn.close()
    return jsonify([row["room_type"] for row in rows])

@app.route("/api/rooms/<room_type>", methods=["GET"])
def get_rooms_by_type(room_type):
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT room_number FROM residents WHERE room_type = ? ORDER BY room_number", (room_type,)).fetchall()
    conn.close()
    return jsonify([row["room_number"] for row in rows])

@app.route("/api/residents_by_room/<room_number>", methods=["GET"])
def get_residents_by_room(room_number):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM residents WHERE room_number = ?", (room_number,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/api/residents", methods=["POST"])
def add_resident():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.execute(
        '''
        INSERT INTO residents 
        (name, room_number, room_type, phone, alt_phone, aadhar, join_date, amount_paid, due_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            data["name"],
            data["room_number"],
            data["room_type"],
            data["phone"],
            data.get("alt_phone"),
            data["aadhar"],
            data["join_date"],
            data["amount_paid"],
            data["due_date"]
        )
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"status": "success", "id": new_id}), 201

@app.route("/api/residents/<int:resident_id>", methods=["PUT"])
def update_resident(resident_id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        '''
        UPDATE residents 
        SET name=?, room_number=?, room_type=?, phone=?, alt_phone=?, aadhar=?, join_date=?, amount_paid=?, due_date=?
        WHERE id=?
        ''',
        (
            data["name"],
            data["room_number"],
            data["room_type"],
            data["phone"],
            data.get("alt_phone"),
            data["aadhar"],
            data["join_date"],
            data["amount_paid"],
            data["due_date"],
            resident_id
        )
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route("/api/residents/<int:resident_id>", methods=["DELETE"])
def delete_resident(resident_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM residents WHERE id=?", (resident_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# New endpoint for residents whose due date is within next 2 days, including room_type info
@app.route("/api/residents_due_soon", methods=["GET"])
def residents_due_soon():
    conn = get_db_connection()
    today = datetime.now().date()
    two_days_later = today + timedelta(days=2)

    rows = conn.execute(
        "SELECT * FROM residents WHERE due_date BETWEEN ? AND ? ORDER BY due_date ASC",
        (today.isoformat(), two_days_later.isoformat())
    ).fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    create_table()
    app.run(debug=True)
