import sqlite3

DB_NAME = "appointments.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        doctor TEXT,
        date TEXT,
        reason TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_appointment(name, doctor, date, reason):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO appointments (name, doctor, date, reason)
    VALUES (?, ?, ?, ?)
    """, (name, doctor, date, reason))

    conn.commit()
    conn.close()


def get_appointments():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, doctor, date, reason FROM appointments")
    rows = cursor.fetchall()

    conn.close()
    return rows


def delete_appointment(appt_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments WHERE id = ?", (appt_id,))

    conn.commit()
    conn.close()


def is_doctor_available(doctor, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM appointments
    WHERE doctor = ? AND date = ?
    """, (doctor, date))

    count = cursor.fetchone()[0]
    conn.close()

    return count == 0