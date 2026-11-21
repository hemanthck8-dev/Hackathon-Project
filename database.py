"""
MediCare – Database Module
SQLite database for storing medicines, history, and settings.
"""

import sqlite3
import os
from datetime import datetime, date


DB_NAME = "medicare.db"


def get_db_path():
    """Get the database path, using app storage on Android."""
    try:
        from android.storage import app_storage_path  # noqa: F401
        return os.path.join(app_storage_path(), DB_NAME)
    except ImportError:
        return DB_NAME


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            frequency TEXT NOT NULL DEFAULT 'daily',
            notes TEXT DEFAULT '',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER NOT NULL,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            scheduled_time TEXT NOT NULL,
            action TEXT NOT NULL,
            action_time TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            scheduled_date TEXT NOT NULL,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Insert default settings if not exists
    defaults = [
        ("notifications_enabled", "1"),
        ("reminder_sound", "1"),
        ("reminder_vibrate", "1"),
        ("snooze_minutes", "5"),
    ]
    for key, value in defaults:
        cursor.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )

    conn.commit()
    conn.close()


# --------------- Medicine CRUD ---------------

def add_medicine(name, dosage, reminder_time, start_date, end_date, frequency, notes):
    """Add a new medicine to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO medicines
           (name, dosage, reminder_time, start_date, end_date, frequency, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, dosage, reminder_time, start_date, end_date or "", frequency, notes or ""),
    )
    conn.commit()
    med_id = cursor.lastrowid
    conn.close()
    return med_id


def update_medicine(med_id, name, dosage, reminder_time, start_date, end_date, frequency, notes):
    """Update an existing medicine."""
    conn = get_connection()
    conn.execute(
        """UPDATE medicines
           SET name=?, dosage=?, reminder_time=?, start_date=?,
               end_date=?, frequency=?, notes=?
           WHERE id=?""",
        (name, dosage, reminder_time, start_date, end_date or "", frequency, notes or "", med_id),
    )
    conn.commit()
    conn.close()


def delete_medicine(med_id):
    """Delete a medicine by ID."""
    conn = get_connection()
    conn.execute("DELETE FROM medicines WHERE id=?", (med_id,))
    conn.commit()
    conn.close()


def get_all_medicines():
    """Get all active medicines ordered by reminder time."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM medicines WHERE active=1 ORDER BY reminder_time ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_medicine_by_id(med_id):
    """Get a single medicine by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM medicines WHERE id=?", (med_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_todays_medicines():
    """Get medicines scheduled for today based on frequency and date range."""
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    day_name = today.strftime("%A").lower()

    all_meds = get_all_medicines()
    todays = []

    for med in all_meds:
        # Check date range
        start = med.get("start_date", "")
        end = med.get("end_date", "")

        if start and today_str < start:
            continue
        if end and end.strip() and today_str > end:
            continue

        # Check frequency
        freq = med.get("frequency", "daily").lower()
        if freq == "daily":
            todays.append(med)
        else:
            # Frequency is comma-separated day names
            days = [d.strip().lower() for d in freq.split(",")]
            if day_name in days:
                todays.append(med)

    return todays


def get_upcoming_medicines(limit=5):
    """Get upcoming medicines for today that haven't been taken yet."""
    now = datetime.now().strftime("%H:%M")
    today_str = date.today().strftime("%Y-%m-%d")

    todays = get_todays_medicines()
    upcoming = []

    for med in todays:
        if med["reminder_time"] >= now:
            # Check if already taken today
            if not is_medicine_handled_today(med["id"], today_str):
                upcoming.append(med)

    upcoming.sort(key=lambda m: m["reminder_time"])
    return upcoming[:limit]


# --------------- History ---------------

def record_action(medicine_id, medicine_name, dosage, scheduled_time, action):
    """Record a taken or skipped action."""
    conn = get_connection()
    today_str = date.today().strftime("%Y-%m-%d")
    conn.execute(
        """INSERT INTO history
           (medicine_id, medicine_name, dosage, scheduled_time, action, scheduled_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (medicine_id, medicine_name, dosage, scheduled_time, action, today_str),
    )
    conn.commit()
    conn.close()


def is_medicine_handled_today(medicine_id, today_str=None):
    """Check if medicine has been taken or skipped today."""
    if today_str is None:
        today_str = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM history WHERE medicine_id=? AND scheduled_date=?",
        (medicine_id, today_str),
    ).fetchone()
    conn.close()
    return row["cnt"] > 0


def get_history(limit=50):
    """Get medicine history records, most recent first."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM history
           ORDER BY action_time DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_history_by_date(target_date):
    """Get history for a specific date."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM history WHERE scheduled_date=? ORDER BY scheduled_time ASC",
        (target_date,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_adherence_stats():
    """Calculate adherence statistics."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as cnt FROM history").fetchone()["cnt"]
    taken = conn.execute(
        "SELECT COUNT(*) as cnt FROM history WHERE action='taken'"
    ).fetchone()["cnt"]
    skipped = conn.execute(
        "SELECT COUNT(*) as cnt FROM history WHERE action='skipped'"
    ).fetchone()["cnt"]
    conn.close()

    rate = round((taken / total) * 100, 1) if total > 0 else 0
    return {
        "total": total,
        "taken": taken,
        "skipped": skipped,
        "adherence_rate": rate,
    }


# --------------- Settings ---------------

def get_setting(key, default=""):
    """Get a setting value."""
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    """Set a setting value."""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, str(value)),
    )
    conn.commit()
    conn.close()


def get_medicine_count():
    """Get total count of active medicines."""
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM medicines WHERE active=1"
    ).fetchone()
    conn.close()
    return row["cnt"]
